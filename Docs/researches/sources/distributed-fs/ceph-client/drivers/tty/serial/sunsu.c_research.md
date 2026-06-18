# sources/distributed-fs/ceph-client/drivers/tty/serial/sunsu.c

## Purpose
This driver supports Sun SU UARTs, largely 8250-family devices used as serial ports and sometimes as keyboard/mouse interfaces. It provides both normal tty serial behavior and `serio` integration for Sun keyboard/mouse ports.

## Important APIs, Types, And Functions
`struct uart_sunsu_port` embeds `uart_port` and tracks ACR/IER/LCR, detected UART type, SU role, register size, cached cflag, break flags, and optional serio state. `sunsu_pops` is the uart-core operation table for normal serial ports.

`serial_in()`/`serial_out()` abstract IO-space, hub6, and MMIO access, including a sparc32 MCR OUT2 workaround. `sunsu_autoconfig()` performs 8250-compatible existence, loopback, FIFO, StarTech, 16750, and scratch-register tests. `receive_chars()` and `transmit_chars()` implement normal tty RX/TX; `receive_kbd_ms_chars()` and `sunsu_kbd_ms_interrupt()` handle keyboard/mouse devices and mouse auto-baud using `suncore_mouse_baud_detection()`.

## Control Flow
Init counts OF `su`, `su_pnp`, and compatible `serial` nodes that are true serial ports, registers Sun minors, and registers the platform driver. `su_probe()` classifies a node through `/aliases` as keyboard, mouse, or serial. Keyboard/mouse devices allocate private state, initialize baud and serio, start the UART, and do not register a tty port. Serial devices use a static `sunsu_ports` entry, autoconfigure the UART, match possible console nodes, and call `uart_add_one_port()`.

For tty ports, `startup()` initializes special 16C950/RSA paths, clears FIFOs and interrupt registers, requests a shared IRQ, sets MCR, enables RX/status interrupts, and clears registers again. The serial interrupt loops until IIR reports no interrupt, handling RX, modem deltas, TX, and flip push.

## State And Persistence
Global state includes `sunsu_ports[UART_NR]` and `nr_inst`. Keyboard/mouse ports allocate separate state and optional serio registration. Per-port cached state includes IER, LCR, cflag, detected type, and line status break flags. No state is persisted outside memory.

## Dependencies And Integration Points
The driver depends on OF/platform resources, SPARC IRQ setup, serial core, tty flip buffers, console/sysrq, optional serio, `serial_reg.h`, optional RSA support, and `suncore` helpers. Console setup gets firmware termios through `sunserial_console_termios()`.

## Risks
The driver mixes legacy 8250 probing with platform OF enumeration and has several hardware-specific special cases. `nr_inst` is shared by serial and keyboard/mouse probes, so ordering matters. Keyboard/mouse ports bypass uart registration but still use startup/IRQ paths. Autoconfig writes many legacy UART registers and can misdetect quirky devices. Busy waits in serio write and console output can stall if hardware stops reporting THRE/TEMT.

## Test Signals
Test normal tty ports and keyboard/mouse aliases separately, autoconfig across 16450/16550A/16750/16C950-like hardware, shared IRQ behavior, RX error/break/sysrq handling, modem deltas, termios divisor/FIFO changes, console output with firmware settings, serio open/close/write, mouse baud rotation, and probe/remove cleanup for allocated keyboard/mouse state.
