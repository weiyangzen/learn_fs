# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/Makefile

Purpose: Connects the Microchip wireless directory to the kernel build by descending into the WILC1000 subdirectory when `CONFIG_WILC1000` is enabled.

Important APIs and entries: `obj-$(CONFIG_WILC1000) += wilc1000/` is the only build rule.

Control flow: Kbuild evaluates the object directory rule and includes the child Makefile only for enabled WILC1000 builds.

State and persistence: No runtime state. Build output depends on `.config`.

Dependencies and integration points: Depends on child `wilc1000/Makefile` for actual object lists and bus-specific modules.

Risks: Since both SDIO and SPI select `WILC1000`, this top-level rule must remain keyed to the core symbol or bus-specific builds would miss shared objects.

Test signals: `CONFIG_WILC1000_SDIO=m/y` and `CONFIG_WILC1000_SPI=m/y` builds should enter this directory and compile the core plus bus objects.
