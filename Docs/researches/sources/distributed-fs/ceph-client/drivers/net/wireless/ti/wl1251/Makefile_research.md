# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/Makefile

Purpose: Defines wl1251 module composition for Kbuild.

Important APIs, types, and functions: The core `wl1251.o` is built from `main.o event.o tx.o rx.o ps.o cmd.o acx.o boot.o init.o debugfs.o io.o`. Bus modules add `spi.o` and `sdio.o` for `wl1251_spi.o` and `wl1251_sdio.o`.

Control flow: `obj-$(CONFIG_WL1251)` emits the core object; bus objects are emitted when their config symbols are enabled.

State and persistence: Build-time only.

Dependencies and integration points: Aligns with Kconfig symbols and links the files researched here into the core wl1251 module.

Risks: A missing object in `wl1251-objs` causes unresolved symbols or absent functionality, especially command/ACX/boot/debugfs/event support.

Test signals: Module link tests for `wl1251`, `wl1251_spi`, and `wl1251_sdio`.
