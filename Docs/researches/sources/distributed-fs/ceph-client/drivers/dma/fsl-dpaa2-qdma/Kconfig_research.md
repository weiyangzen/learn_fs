# sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Kconfig Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Kconfig

### Purpose
This Kconfig entry exposes the NXP DPAA2 QDMA driver as `CONFIG_FSL_DPAA2_QDMA`. It restricts the driver to ARM64 systems with the Freescale Management Complex bus and DPIO services, and it selects the DMAengine and virtual-channel support needed by the implementation.

### Important APIs, Types, And Functions
The single symbol is `FSL_DPAA2_QDMA`, a tristate menuconfig labeled `"NXP DPAA2 QDMA"`. It depends on `ARM64`, `FSL_MC_BUS`, and `FSL_MC_DPIO`, and selects `DMA_ENGINE` plus `DMA_VIRTUAL_CHANNELS`.

### Control Flow, State, And Persistence
There is no runtime state. Build-time selection controls whether `dpaa2-qdma.o` and `dpdmai.o` are compiled and whether the DPAA2 QDMA MC-bus driver can register at late init.

### Dependencies, Integration Points, Risks, And Test Signals
The entry integrates the driver with the kernel configuration system and prevents builds without MC bus or DPIO notification APIs. Risks are mostly configuration drift: missing dependencies would produce link errors, while overly narrow dependencies would hide the driver from valid platforms. Test signals include allmodconfig/allyesconfig coverage on ARM64, disabled dependency builds, module and built-in builds, and successful selection of virtual DMA channel helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/Kconfig -->
