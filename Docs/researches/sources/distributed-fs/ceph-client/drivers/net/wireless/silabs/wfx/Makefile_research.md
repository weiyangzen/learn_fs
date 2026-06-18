# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/Makefile

Purpose: Builds the Silicon Labs WFx aggregate driver object and selects bus-specific source files.

Important APIs and types: `wfx-y` lists core objects: bottom half, HW I/O, firmware loader, HIF MIB/TX/RX, queues, data TX/RX, scan, station callbacks, key handling, main probe, and debugfs/trace helpers. `wfx-$(CONFIG_SPI)` adds `bus_spi.o`; `wfx-$(subst m,y,$(CONFIG_MMC))` adds `bus_sdio.o` even when MMC is modular. `CFLAGS_debug.o = -I$(src)` supports local tracepoint include generation.

Control flow and integration: Kbuild links the listed objects into `wfx.o`, then `obj-$(CONFIG_WFX) += wfx.o` emits a built-in or module. Conditional bus objects provide the external `wfx_spi_driver` and `wfx_sdio_driver` symbols used by `main.c`.

State and persistence: No runtime state, but object inclusion decides which bus registration paths exist.

Dependencies: Depends on `CONFIG_WFX`, `CONFIG_SPI`, and `CONFIG_MMC`; also relies on `debug.c` defining tracepoints with local include paths.

Risks and test signals: Risks include unresolved bus driver symbols if Makefile conditions drift from `main.c` registration checks. Build tests should cover SPI-only, SDIO-only, both buses, module and built-in combinations, and tracepoint compilation.

Test signals: Source read size: 25 lines, 434 bytes.
