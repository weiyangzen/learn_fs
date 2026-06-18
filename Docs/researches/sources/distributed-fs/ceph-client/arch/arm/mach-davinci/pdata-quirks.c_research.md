# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pdata-quirks.c

Purpose: supplies legacy platform-data registration for DA850 boards still described by DT but requiring non-DT media subdevice details.

Important APIs/types/functions: `struct pdata_init`, TVP5146 and ADV7343 platform data, VPIF capture/display configs, `pdata_quirks_check()`, board-specific init functions, and `pdata_quirks_init()`.

Control flow: late init scans compatible strings such as `ti,da850-lcdk` and `ti,da850-evm`; matching entries register VPIF capture/display devices with board-specific subdevice and route data.

State and persistence: static platform data structures are handed to VPIF platform devices and persist for driver probing.

Dependencies and integration: integrates media I2C subdevices, VPIF platform APIs from `da850.c`, OF machine compatibility, and legacy board support.

Risks: this bridges old platform data into DT boot, so it can conflict with future full-DT descriptions if both instantiate devices. Shared static config is mutated for LCDK by reducing subdevice count.

Test signals: DA850 EVM/LCDK video capture/display probe, I2C subdevice detection at expected addresses, and absence of duplicate media device registration.
