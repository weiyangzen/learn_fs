<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/devices.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/devices.c

Purpose: Common OMAP1 platform-device registration. It creates RTC, MMC, uWire SPI, RNG, watchdog, SRAM/clock late-init, and associated resources depending on configuration and CPU type.

Important APIs/types/functions: Important functions are `omap1_init_mmc`, `omap_mmc_add`, `omap1_mmc_mux`, `omap1_init_devices`, `omap_init_wdt`, and internal RTC/uWire/RNG init helpers.

Control flow, state, and persistence: State is static platform devices/resources plus per-board MMC platform data patched with features and `dev` pointers. The arch initcall runs after board init to initialize SRAM, late clocks, and on-chip devices.

Dependencies and integration points: Important functions are `omap1_init_mmc`, `omap_mmc_add`, `omap1_mmc_mux`, `omap1_init_devices`, `omap_init_wdt`, and internal RTC/uWire/RNG init helpers. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP mux/registers, clock/SRAM, platform data headers, RTC/MMC/uWire/RNG/watchdog drivers, and CPU detection. Risks are board data mutation, hard-coded DMA request numbers, late clock timing, and optional config stubs. Test MMC controllers 0/1, RTC alarms, RNG on OMAP16xx, watchdog reset-source data, and arch init ordering.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 363 lines, 8448 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/devices.c -->
