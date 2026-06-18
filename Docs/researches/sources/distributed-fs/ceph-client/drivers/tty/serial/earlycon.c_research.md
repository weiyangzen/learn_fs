# sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon.c

Purpose: generic serial early console framework. It parses `earlycon=` and `console=` early parameters, maps MMIO/I/O resources, matches earlycon table entries, initializes `earlycon_device`, supports OF early console setup, and registers the boot console.

Important APIs/types/functions: global `early_con` and `early_console_dev`; `setup_earlycon()`; `register_earlycon()`; `parse_options()`; `of_setup_earlycon()`; `param_setup_earlycon()`; `param_setup_earlycon_console_alias()`; and `earlycon_acpi_spcr_enable`.

Control flow: early params invoke setup. Named earlycon strings are matched against `__earlycon_table`, preferring generic entries before compatible-specific entries. Addressed forms are parsed into `uart_port` iotype/address/options and MMIO is mapped. Provider setup must install `con->write` before the console is registered. OF setup translates node address and applies `reg-offset`, `reg-shift`, `reg-io-width`, endian, speed, and clock properties.

State/persistence: one global boot console/device holds parsed options, baud, uartclk, iotype, mapbase/membase, and ACPI SPCR flag. The console is `CON_BOOT` and intended for early boot handoff.

Dependencies/integration: console core, serial core, early params, fixmap or ioremap, OF flattened tree, optional ACPI SPCR, architecture `BASE_BAUD`, and earlycon provider declarations.

Risks: only one early console can register. Mapping size is fixed in some paths. Malformed options can be passed to provider setup by design. OF width/endian mistakes can corrupt early accesses. Early boot context limits recovery.

Test signals: all parameter forms, duplicate registration, empty `earlycon` with DT/ACPI, `console=uart...` alias, MMIO/I/O width/endian parsing, provider failure, and OF `stdout-path` options.
