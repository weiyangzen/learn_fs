# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-lpt.c

Purpose: provides an optional legacy parallel-port ByteBlaster JTAG bit-banging backend for the Altera STAPL module.

Important APIs and functions: `netup_jtag_io_lpt(void *device, int tms, int tdi, int read_tdo)` is the exported callback-compatible entry point. Internal helpers `byteblaster_write` and `byteblaster_read` wrap `outb` and `inb` at offsets relative to base port `0x378`.

Control flow: the first callback initializes the LPT control port once by setting control bits. Each call builds a data byte from TDI and TMS, writes it, optionally reads inverted TDO from the status port, pulses TCK by setting bit 0, then drops it.

State and persistence: a single static `lpt_hardware_initialized` flag persists for the module lifetime. The hardware port state is mutated directly and is not restored on module exit in this file.

Dependencies and integration points: built only when `CONFIG_HAS_IOPORT` is available. It is selected by `altera_init` when no board-specific JTAG callback is provided and the architecture supports port I/O.

Risks: the `device` argument is unused and the base port is hard-coded to `0x378`, so it is not safe for arbitrary parallel-port configurations. There is no locking around the global initialization flag or port access. Direct I/O port use can conflict with other parallel-port users.

Test signals: compile on `CONFIG_HAS_IOPORT` platforms, oscilloscope or logic-analyzer validation of TMS/TDI/TCK/TDO timing, and negative tests confirming non-I/O-port builds do not reference this backend.
