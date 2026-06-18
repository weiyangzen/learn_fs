# sources/distributed-fs/ceph-client/drivers/ssb/Kconfig

## Purpose
Configuration menu for Sonics Silicon Backplane support, host transports, built-in SSB core drivers, embedded support, and optional GPIO/flash/PCI bridge facilities.

## Important APIs, Types, and Functions
This file defines Kconfig symbols rather than C APIs. Core symbols include `SSB`, `SSB_SPROM`, `SSB_BLOCKIO`, host options `SSB_PCIHOST`, `SSB_PCMCIAHOST`, `SSB_SDIOHOST`, `SSB_HOST_SOC`, built-in drivers `SSB_DRIVER_PCICORE`, `SSB_DRIVER_MIPS`, `SSB_DRIVER_EXTIF`, `SSB_DRIVER_GIGE`, `SSB_DRIVER_GPIO`, and feature gates `SSB_SERIAL`, `SSB_SFLASH`, `SSB_EMBEDDED`, `SSB_PCICORE_HOSTMODE`.

## Control Flow
Dependency flow starts with `SSB_POSSIBLE` requiring I/O memory and DMA. `menuconfig SSB` gates all child symbols. Host support is enabled when the relevant subsystem can be built in or as SSB-compatible. Several options select shared support: PCI/PCMCIA/SoC select `SSB_SPROM`; MIPS selects `SSB_SERIAL` and `SSB_SFLASH`; GPIO selects `IRQ_DOMAIN` on embedded builds.

## State and Persistence
Kconfig output persists in the kernel `.config` and controls which object files, code paths, exports, and platform devices are compiled.

## Dependencies and Integration Points
Integrates with PCI, PCMCIA, MMC/SDIO, BCM47XX NVRAM, MIPS, GPIOLIB, and IRQ_DOMAIN. It also coordinates with `Makefile` object selection and preprocessor guards in all SSB files.

## Risks
Wrong dependency combinations can silently omit host support or built-in system core drivers. `SSB_EMBEDDED` depends on MIPS and either no PCI or PCI core hostmode, so embedded watchdog/GPIO/flash behavior is tightly coupled to board architecture. `SSB_B43_PCI_BRIDGE` is hidden and depends on `SSB_PCIHOST`, so wireless bridge registration depends on selecting it elsewhere.

## Test Signals
Validate representative configs: PCI-host wireless, PCMCIA-host wireless, BCM47xx SoC/MIPS, GPIO-only, and SDIO. Build logs should include only expected `ssb-*` objects and no unresolved symbols from disabled transports.
