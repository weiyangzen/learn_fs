# sources/distributed-fs/ceph-client/drivers/video/console/Makefile

Purpose: build mapping for Linux graphics console drivers.

Important APIs/types/functions: object lines map `CONFIG_DUMMY_CONSOLE` to `dummycon.o`, `CONFIG_SGI_NEWPORT_CONSOLE` to `newport_con.o`, `CONFIG_STI_CONSOLE` to `sticon.o`, `CONFIG_VGA_CONSOLE` to `vgacon.o`, and `CONFIG_MDA_CONSOLE` to `mdacon.o`.

Control flow: no runtime flow. Kbuild includes each object according to the corresponding config symbol.

State and persistence: build artifacts persist in the kernel build tree; no source-level runtime state.

Dependencies and integration: paired with the console Kconfig symbols and the kernel Kbuild object-selection mechanism.

Risks: stale or incorrect object mappings would silently omit or include console drivers, affecting boot consoles. Test signals are `make drivers/video/console/` or full kernel build checks with each symbol combination, plus ensuring modular `MDA_CONSOLE` still produces `mdacon`.
