<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/serial.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/serial.c

Purpose: Registers board-specific 8250 serial port data after machtype and UART base detection.

Important APIs/types/functions: `PORT` and `PORT_M` macros build `plat_serial8250_port` entries. `serial_init()` fills IO or memory base and registers `serial8250`; `serial_exit()` unregisters it.

Control flow: Selects one table entry by `mips_machtype`. Memory-mapped UARTs use `loongson_uart_base` and `_loongson_uart_base`; port-mapped UARTs compute `iobase` relative to `LOONGSON_PCIIO_BASE`. The following table entry is zeroed as the 8250 terminator.

State and persistence: Registers a platform serial device and mutates the selected table entry with the detected base.

Dependencies and integration: Depends on `uart_base.c` for early base selection and on the 8250 platform driver.

Risks: Out-of-range `mips_machtype` would index the table incorrectly. Clock rates and IRQs are hard-coded per board.

Test signals: Console and ttyS device should appear with the expected IO type, IRQ, and UART clock for each machine type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/serial.c -->
