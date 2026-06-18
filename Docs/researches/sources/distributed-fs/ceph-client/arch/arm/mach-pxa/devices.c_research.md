<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.c

Purpose: central legacy platform-device catalog and registration helpers for PXA machines.

Important APIs and objects: `pxa_register_device()` assigns platform data and registers a `platform_device`. Setup helpers include `pxa_set_mci_info()`, UART info setters, `pxa_set_fb_info()`, `pxa_set_i2c_info()`, `pxa_set_ohci_info()`, `pxa2xx_set_dmac_info()`, and `pxa_register_wdt()`. Exported device objects cover PMU, MMC, UDC variants, framebuffer, FFUART/BTUART/STUART/HWUART, I2C, I2S, ASoC SSP/PCM, RTC, PWM, SSP, OHCI, GPIO, and DMA.

Control flow: SoC init files add arrays of these platform devices for non-DT boots. Board files call setters to register optional devices with board-specific platform data. `pxa_set_mci_info()` uses `platform_device_register_full()` so platform data and properties can be copied atomically. `pxa_register_wdt()` registers a `sa1100_wdt` resource over the OS timer and passes reset status.

State and persistence: static resources, DMA masks, and platform devices persist for the life of the kernel. Setters mutate `.dev.platform_data` and sometimes parent pointers before registration.

Dependencies and integration: relies on PXA IRQ constants, fixed physical addresses, platform data headers for MMC/I2C/OHCI/fb/UDC, GPIO wake helpers, and DMAengine slave maps from SoC files.

Risks and test signals: legacy static platform devices can only be registered once; repeated setters may fail. `pxa_set_hwuart_info()` silently ignores non-PXA255 hardware. Test with non-DT PXA25x/PXA27x boot, device tree boot not registering duplicates, platform resource ranges, and driver probes for expected devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.c -->
