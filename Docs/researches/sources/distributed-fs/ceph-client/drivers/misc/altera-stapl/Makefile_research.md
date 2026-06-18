# sources/distributed-fs/ceph-client/drivers/misc/altera-stapl/Makefile

Purpose: maps `CONFIG_ALTERA_STAPL` to the objects that form the Altera STAPL firmware download module.

Important APIs and entries: `altera-stapl-y` links `altera-jtag.o`, `altera-comp.o`, and `altera.o`. `altera-stapl-$(CONFIG_HAS_IOPORT)` adds `altera-lpt.o` only when port I/O is available. `obj-$(CONFIG_ALTERA_STAPL)` emits `altera-stapl.o`.

Control flow: kbuild combines the interpreter, decompressor, and JTAG state-machine implementation into one module. The optional LPT implementation supplies the fallback `netup_jtag_io_lpt` function declared in `altera-exprt.h`.

State and persistence: no runtime state. Build composition changes depending on architecture support for I/O ports.

Dependencies and integration points: depends on the local Kconfig symbol and on the source files exporting matching symbols. It integrates with board drivers that link against `altera_init`.

Risks: builds without `CONFIG_HAS_IOPORT` still compile declarations for the LPT fallback, but `altera_init` must avoid using that fallback when port I/O is disabled. Adding new interpreter support requires updating this object list.

Test signals: build with `ALTERA_STAPL=y/m` on I/O-port and non-I/O-port architectures, and verify unresolved-symbol checks for `netup_jtag_io_lpt` do not fail.
