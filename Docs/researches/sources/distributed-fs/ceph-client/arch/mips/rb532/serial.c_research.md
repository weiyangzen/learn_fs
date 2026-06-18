# sources/distributed-fs/ceph-client/arch/mips/rb532/serial.c

Purpose: early 8250 serial setup for RB532 console configurations.

Important APIs and control flow: a static `uart_port` describes UART0 at `REGBASE + UART0BASE`, KSEG1 mapped, with `UART0_IRQ`, memory I/O, and register shift 2. `setup_serial_port()` sets `uartclk` from exported `idt_cpu_freq` and calls `early_serial_setup()` as an `arch_initcall()`.

State, persistence, and integration: it registers one early serial port and depends on PROM parsing CPU frequency before arch initcalls. Integration is with the 8250 serial core and console support. Risks include duplicate registration with the platform `serial8250` device in `devices.c`, wrong baud if firmware frequency is absent or bad, and no failure logging. Test signals are early console output, ttyS0 registration, and correct baud behavior.
