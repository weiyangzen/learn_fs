# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/ls_uart.c

Purpose: Linkstation AVR UART helper used for watchdog disarm and board restart/poweroff commands.

Important APIs and control flow: `ls_uarts_init` locates `/soc10x/serial@80004500`, reads `clock-frequency`, maps the UART, initializes it, and schedules `wd_stop`. `avr_uart_configure` programs 8-bit serial with stop/parity settings and a 9600 baud divisor. `avr_uart_send` writes each command byte four times. `wd_stop` sends a fixed watchdog-disarm sequence in chunks when the transmitter is ready and prints any response bytes.

State, dependencies, and risks: state is global `avr_addr`, `avr_clock`, and delayed work. Dependencies include NS16550 register layout, OF serial node path, workqueues, and Linkstation board hooks. Risks include unchecked `of_get_property` dereference for `clock-frequency`, no synchronization around UART use after init, and command loops in restart/poweroff if AVR is absent. Test signals are watchdog disarm response, reboot/poweroff via AVR, and no serial conflict with `CONFIG_SERIAL_8250`.
