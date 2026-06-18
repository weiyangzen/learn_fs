# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/serial-sh7722.c

Purpose: provides SH7722-specific SCI pin initialization for the first SCIF port.

Important APIs, types, and functions: `sh7722_sci_init_pins()` implements `struct plat_sci_port_ops.init_pins`. `sh7722_sci_port_ops` is exported as a global platform ops structure. The function edits the PSCR register at `0xa405011e`.

Control flow: the SCI core calls `.init_pins` with a `uart_port` and termios `cflag`. If `port->mapbase == 0xffe00000`, the code clears PSCR bits `0x03cf`; when hardware flow control is not requested (`!(cflag & CRTSCTS)`), it sets `0x0340`, then writes PSCR.

State and persistence: no software state is stored; the persistent effect is a PFC/serial pin register write. Pin state may be overwritten by later PFC changes or resume restoration.

Dependencies and integration points: depends on `linux/serial_sci.h`, `linux/serial_core.h`, raw MMIO, and SH7722 serial platform data that attaches `sh7722_sci_port_ops` to the relevant port.

Risks: the hook only handles one mapbase and uses hard-coded PSCR bits. Incorrect `cflag` handling can disable RTS/CTS or select conflicting pins. It bypasses generic pinctrl abstractions.

Test signals: opening SCIF0 with and without `CRTSCTS` should drive correct pins; serial loopback and hardware-flow-control tests should pass on SH7722 boards.
