# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/altera-exprt.h

Purpose: declares cross-file helper exports for the Altera STAPL module.

Important APIs and types: declares `altera_shrink` for compressed firmware data expansion and `netup_jtag_io_lpt` for the optional ByteBlaster-style parallel-port JTAG fallback.

Control flow: `altera.c` includes this header to call the decompressor and, when no board-specific `jtag_io` callback is provided and I/O ports are enabled, to install the LPT JTAG callback. `altera-comp.c` and `altera-lpt.c` provide the definitions.

State and persistence: the header owns no state. The declared functions operate on caller-provided buffers or on external hardware through a callback-style interface.

Dependencies and integration points: relies on Linux fixed-width types being available. It is internal to the `altera-stapl` module and forms a narrow boundary between interpreter, compression, and optional LPT transport code.

Risks: `netup_jtag_io_lpt` is declared unconditionally even though the object defining it is built only with `CONFIG_HAS_IOPORT`; callers must keep the runtime guard correct. There are no comments documenting `altera_shrink` buffer ownership or bounds expectations.

Test signals: module link checks with and without `CONFIG_HAS_IOPORT`, decompressor unit-style fixture coverage through `altera_init`, and hardware tests for fallback LPT JTAG where supported.
