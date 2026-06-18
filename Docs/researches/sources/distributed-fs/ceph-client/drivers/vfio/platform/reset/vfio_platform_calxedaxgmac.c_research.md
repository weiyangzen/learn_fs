<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_calxedaxgmac.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_calxedaxgmac.c

## Purpose
This file provides a deprecated reset handler for Calxeda XGMAC platform devices with compatible string `calxeda,hb-xgmac`. It quiesces the MAC and DMA engines so the device can be safely handed to VFIO userspace or released.

## Important APIs, types, and functions
The main callback is `vfio_platform_calxedaxgmac_reset()`. `xgmac_mac_disable()` clears DMA transmit/receive start bits and MAC TX/RX enable bits. Register constants cover MAC control, DMA control, and DMA interrupt enable.

## Control flow
The reset handler logs deprecation once, maps region 0 if needed, writes zero to `XGMAC_DMA_INTR_ENA` to disable DMA interrupts, then calls `xgmac_mac_disable()` to stop TX/RX at DMA and MAC levels.

## State and persistence behavior
The only software state is a cached region mapping. Hardware state persists as disabled interrupts and disabled TX/RX engines. There is no polling or explicit full hardware reset.

## Dependencies and integration points
It depends on VFIO platform region metadata, Linux MMIO accessors, and the reset-handler registration macro. The common platform code discovers it by `compatible` and calls it during init/open/close/reset operations.

## Risks and test signals
Risks include incomplete reset semantics, reliance on region 0, and no verification that the MAC has actually stopped. Test signals include matching module alias, ioremap failure handling, interrupt masking verification, and repeated VFIO open/close assignment tests on Calxeda XGMAC hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_calxedaxgmac.c -->
