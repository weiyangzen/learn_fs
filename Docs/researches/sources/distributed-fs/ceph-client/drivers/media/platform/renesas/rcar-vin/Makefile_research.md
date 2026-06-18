# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/Makefile

## Purpose
This Makefile builds the R-Car VIN capture driver composite object.

## Important APIs, Types, And Functions
It declares `rcar-vin-objs = rcar-core.o rcar-dma.o rcar-v4l2.o` and links `rcar-vin.o` when `CONFIG_VIDEO_RCAR_VIN` is enabled.

## Control Flow
Kbuild compiles the core platform/media graph file, DMA/vb2 hardware file, and V4L2 ioctl/file-operations file into a single driver object or module.

## State And Persistence
No runtime state exists. The Makefile only controls build composition.

## Dependencies And Integration Points
It integrates the three VIN implementation slices that share declarations from `rcar-vin.h`.

## Risks
Adding new VIN source files without updating this list would omit functionality. Removing one of the three current objects would break exported-internal calls across the driver.

## Test Signals
Build as built-in and module, verify all three objects are linked, and check that exported-internal symbols referenced across the three files resolve.
