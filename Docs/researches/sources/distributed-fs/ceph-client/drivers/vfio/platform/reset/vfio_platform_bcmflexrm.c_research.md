<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_bcmflexrm.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_bcmflexrm.c

## Purpose
This file provides a deprecated VFIO platform reset handler for Broadcom FlexRM ring manager devices with compatible string `brcm,iproc-flexrm-mbox`. Its purpose is to discover valid ring register blocks and flush them to a quiescent state for device assignment.

## Important APIs, types, and functions
`vfio_platform_bcmflexrm_reset()` is the VFIO reset callback. `vfio_platform_bcmflexrm_shutdown()` disables a single ring, asserts flush state in `RING_CONTROL`, polls `RING_FLUSH_DONE`, then clears flush state and waits for flush-done deassertion. Constants define ring block size, version magic, and register offsets.

## Control flow
Reset logs a deprecation warning, maps region 0 if necessary, then walks the region in `RING_REGS_SIZE` increments. Blocks whose `RING_VER` equals `RING_VER_MAGIC` are treated as rings and passed to the shutdown helper. Individual ring failures are logged and ORed into the final return value while discovery continues.

## State and persistence behavior
The callback caches the MMIO mapping in `vdev->regions[0].ioaddr`. It changes hardware state by disabling rings and forcing flush transitions. No software state survives beyond the cached mapping.

## Dependencies and integration points
It depends on VFIO platform region discovery, relaxed MMIO accessors, polling delays, and reset-handler registration. It integrates with the generic VFIO platform reset lookup by compat alias.

## Risks and test signals
Risks include pointer-range arithmetic over `void __iomem *`, assuming region 0 covers all rings, and returning a bitwise OR of negative errno values rather than the first error. Test signals include multi-ring discovery, timeout paths for flush set/clear, no-ring behavior, and module unload after open/close cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/reset/vfio_platform_bcmflexrm.c -->
