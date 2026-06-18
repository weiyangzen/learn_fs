<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_amdxgbe.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_amdxgbe.c

## Purpose
This file provides a deprecated VFIO platform reset handler for AMD XGBE devices with compatible string `amd,xgbe-seattle-v1a`. It reuses native-driver register knowledge to reset PHY/MAC state before or after VFIO userspace ownership.

## Important APIs, types, and functions
The reset entry point is `vfio_platform_amdxgbe_reset(struct vfio_platform_device *vdev)`. Helper functions `xmdio_read()` and `xmdio_write()` access MDIO MMD registers through the XPCS register window. The handler uses `struct vfio_platform_region` entries 0 and 1 for XGMAC and XPCS MMIO regions.

## Control flow
The handler logs a one-time deprecation warning, ioremaps both required regions if not already mapped, resets the PHY through `MDIO_MMD_PCS/MDIO_CTRL1`, polls up to 50 times with 20 ms sleeps for reset completion, disables auto-negotiation and AN interrupts, clears AN IRQ state, then sets the MAC software reset bit in `DMA_MR` and polls for completion.

## State and persistence behavior
The only persistent runtime state is the cached `ioaddr` mapping stored in the VFIO platform region. Hardware state is modified by disabling AN/interrupts and resetting PHY/MAC logic. The handler returns success even when PHY or MAC reset times out, after logging warnings.

## Dependencies and integration points
It depends on VFIO platform private data, Linux I/O accessors, MDIO constants, and module reset registration through `module_vfio_reset_handler`. It is discovered by `vfio_platform_get_reset()` and called by platform open, close, and reset ioctl paths.

## Risks and test signals
Risks include assuming region ordering, returning success after hardware timeout, and leaving a partially reset device assigned to userspace. Test signals include compat alias autoload, ioremap failure handling, PHY reset polling, DMA reset polling, and assignment open/close cycles on matching AMD XGBE hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_amdxgbe.c -->
