<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.h

Purpose: declaration header for the PXA legacy platform-device catalog.

Important APIs/types: declares exported `struct platform_device` instances from `devices.c`, `pxa_register_device()`, `pxa2xx_set_dmac_info()`, `pxa_set_i2c_info()`, PXA27x/PXA3xx power-I2C setters under config guards, and `PDMA_FILTER_PARAM()` for DMA slave maps.

Control flow and integration: SoC and board files include this header to register predefined device objects or to pass platform data into helper registration paths.

State and persistence: no state directly, but declarations point to static device objects with persistent registration state.

Dependencies: assumes platform-device, software-node, I2C platform data, and MMP DMA types are visible through included C files. Uses `PXAD_PRIO_*` and `struct pxad_param` via the DMA platform headers.

Risks and test signals: config guards must match definitions in `devices.c`; otherwise builds fail for selected SoCs. Test with all PXA config combinations and link checks for referenced platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.h -->
