<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.c

Purpose: legacy ATAGS board support for Gumstix PXA255 motherboards.

Important APIs/functions: `gumstix_init()` configures MFP pins, registers UARTs, initializes Bluetooth, UDC VBUS, MMC, flash, and carrier boards. `gumstix_mmc_init()` registers `pxa2xx-mci`; `gumstix_udc_init()` registers `gpio-vbus` properties; `gumstix_bluetooth_init()` starts the 32 kHz oscillator if needed and toggles BT reset. Weak `am200_init()` and `am300_init()` allow carrier EPD files to override.

Control flow: `MACHINE_START(GUMSTIX)` routes boot to PXA25x mapping, IRQ, timer, and `gumstix_init()`. The init path configures pins then uses device helpers from `devices.c`; carrier init is last.

State and persistence: static flash partitions define bootloader and rootfs layout. GPIO reset state for Bluetooth and registered platform devices persist at runtime.

Dependencies and integration: depends on PXA25x SoC support, MFP pin macros, MTD CFI flash, MMC platform data, `gpio-vbus`, clock/OSCC registers, and optional AM200/AM300 carrier code.

Risks and test signals: carrier boards are not detected programmatically; selected carrier code always runs when built. The Bluetooth clock workaround depends on OSCC status. Test with Gumstix boot, UART probe, flash partitions, MMC card detection, USB VBUS GPIO behavior, Bluetooth reset, and selected carrier initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.c -->
