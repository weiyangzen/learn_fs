# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/Makefile

Purpose: Kbuild definition for CW1200 common and bus-specific modules.

Important APIs and types: `cw1200_core-y` combines `fwio.o`, `txrx.o`, `main.o`, `queue.o`, `hwio.o`, `bh.o`, `wsm.o`, `sta.o`, `scan.o`, and `debug.o`. `cw1200_core-$(CONFIG_PM)` adds `pm.o`. `cw1200_wlan_sdio-y` and `cw1200_wlan_spi-y` define one-object bus modules.

Control flow: `obj-$(CONFIG_CW1200)` emits the core module; SDIO and SPI configs emit front-end modules that call exported core probe/release symbols.

State and persistence: Build-only state.

Dependencies and integration: Mirrors the Kconfig symbols and links common code separately from transport-specific code. Comments include an optional debug CFLAG for `sta.o`.

Risks: Common code and bus modules must agree on exported symbols such as `cw1200_core_probe`, `cw1200_core_release`, `cw1200_irq_handler`, and `cw1200_can_suspend`. Missing a source in `cw1200_core-y` would manifest as unresolved symbols.

Test signals: Module builds should produce `cw1200_core`, `cw1200_wlan_sdio`, and/or `cw1200_wlan_spi` according to config. PM-enabled builds should link suspend/resume handlers.
