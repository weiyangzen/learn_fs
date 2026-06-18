## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_parisc.c

Purpose: PA-RISC GSC serial initialization for Lasi/Asp/Wax/Dino/Timi-style 8250 UARTs. It registers platform-discovered PA-RISC serial hardware with serial8250 and preserves expected tty ordering for some machines.

Important APIs, types, and functions: `serial_init_chip()` maps a PA-RISC device HPA address, derives IRQ and clock, fills `uart_8250_port`, and registers it. Two `parisc_device_id` tables split Lasi-specific systems from the broader serial table. `probe_serial_gsc()` registers `lasi_driver` first and `serial_driver` second to force `ttyS0` ordering where SERIAL_0 is under Lasi and SERIAL_1 under Dino.

Control flow: module init registers both parisc drivers. Each probe validates or synthesizes IRQ, adjusts address by `0x800` except for one sversion, maps 16 bytes, sets `UPIO_MEM`, clock, IRQ, boot autoconfig, and registers the port. There is no remove callback; these are init-time system devices.

State and persistence: no private driver data is stored after successful registration. The ioremap pointer is passed to serial8250. Hardware discovery state comes from PA-RISC device IDs and HPA resources.

Dependencies and integration points: PA-RISC device bus, IOSAPIC serial IRQ helper on 64-bit IOSAPIC builds, architecture I/O mapping, and serial8250 registration.

Risks: no successful-path unmap is present in this file because serial8250 takes over the mapping; teardown is not modeled. IRQ-less devices are ignored or logged depending on parent type. Test signals: boot on Lasi-first and Dino-first systems, tty numbering, IOSAPIC IRQ derivation for sversion `0xad`, address offset handling, and registration failure cleanup with `iounmap()`.
