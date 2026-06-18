<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serial.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/serial.h

Purpose: defines legacy and modern serial port userspace structures for setserial-style configuration, multiport cards, interrupt counters, RS485 mode, and ISO7816 smartcard mode.

Important APIs, types, and functions: `struct serial_struct` carries UART type, line, port, irq, flags, fifo size, custom divisor, baud base, close delays, I/O type, hub6, iomem fields, and map base. Port type and I/O constants cover 8250-class devices and memory/port access modes. `serial_multiport_struct` and `serial_icounter_struct` describe multiport interrupt matching and line counters. `struct serial_rs485` carries RS485 flags, RTS delays, optional address filter/destination, and padding. `struct serial_iso7816` carries ISO7816 flags and timing/clock fields.

Control flow: userspace uses tty ioctls such as TIOCGSERIAL/TIOCSSERIAL, TIOCSRS485/TIOCGRS485, and ISO7816 ioctls to query or modify driver configuration. Drivers sanitize unsupported bits and return the applied state.

State and persistence behavior: serial configuration lives in tty/uart driver state and hardware registers while the port exists. Some legacy settings affect device open/close behavior; RS485/ISO7816 fields affect transmit mode.

Dependencies and integration points: depends on Linux constants/types and `tty_flags.h`. It integrates with the tty layer, 8250 and platform UART drivers, RS485 transceiver control, and userspace tools.

Risks and edge cases: `serial_struct` contains pointer-sized fields and is legacy/architecture-sensitive. RS485 address fields overlap deprecated padding, so callers must not use both. Unsupported RS485/ISO7816 flags should be cleared by drivers rather than silently accepted.

Test signals: TIOCGSERIAL/TIOCSSERIAL compat tests, RS485 enable/RTS/address/bus-termination modes, ISO7816 T parameter and clock settings, unsupported flag sanitization, and open/close delay behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/serial.h -->
