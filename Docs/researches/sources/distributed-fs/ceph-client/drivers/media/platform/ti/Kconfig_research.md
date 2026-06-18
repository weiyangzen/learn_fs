# sources/distributed-fs/ceph-client/drivers/media/platform/ti/Kconfig

## Purpose
Groups Texas Instruments media platform driver configuration and sources the TI subdirectory Kconfig files.

## Important APIs, Types, And Functions
Defines helper symbols `VIDEO_TI_VPDMA`, `VIDEO_TI_SC`, and `VIDEO_TI_CSC`; capture drivers `VIDEO_TI_CAL`, `VIDEO_TI_CAL_MC`, `VIDEO_TI_VIP`, and `VIDEO_TI_J721E_CSI2RX`; and mem2mem driver `VIDEO_TI_VPE` plus debug option `VIDEO_TI_VPE_DEBUG`. It sources AM437x, DaVinci, OMAP, OMAP3 ISP, and other TI Kconfig files.

## Control Flow
Kconfig dependencies and selects determine which TI media drivers are compiled. `VIDEO_TI_CAL_MC` changes CAL default API mode through a module parameter default, while the rest mostly map SoC/feature dependencies to build objects.

## State And Persistence
No runtime state. Kernel `.config` persists selected features and affects available modules and compiled code paths.

## Dependencies And Integration Points
Integrates TI media drivers with V4L2 platform drivers, media controller, subdev API, vb2 DMA-contig, V4L2 fwnode, SOC_DRA7XX, ARCH_K3, Cadence CSI2RX/DPHY, and TI helper modules.

## Risks
Kconfig select/depend drift can create build-only failures, especially under `COMPILE_TEST`. Enabling wrapper drivers like J721E CSI2RX without the underlying Cadence bridge is prevented by dependencies but still requires correct device tree/runtime resources.

## Test Signals
Allmodconfig, allyesconfig, and targeted SoC defconfig builds should cover the matrix. Runtime validation belongs to the specific driver symbols selected here.
