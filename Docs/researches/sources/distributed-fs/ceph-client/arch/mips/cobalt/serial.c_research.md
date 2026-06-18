# sources/distributed-fs/ceph-client/arch/mips/cobalt/serial.c

Purpose: registers the Cobalt 8250 UART as a platform serial device, except on Qube1 where no UART exists.

Important APIs and data: `cobalt_uart_resource` describes MMIO `0x1c800000..0x1c800007` and `SERIAL_IRQ`. `cobalt_serial8250_port` sets `uartclk` 18.432 MHz, `UPIO_MEM`, `UPF_IOREMAP`, `UPF_BOOT_AUTOCONF`, and `UPF_SKIP_TEST`. `cobalt_uart_add()` creates a `serial8250` platform device with `PLAT8250_DEV_PLATFORM`.

State and integration: board ID gates registration; serial pdata persists in the platform device.

Risks and test signals: Qube1 must not register a nonexistent UART. Other boards should expose ttyS with working interrupts and early console continuity from setup.
