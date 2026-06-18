# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_VIDEO_RCAR_VIN`, the Renesas R-Car Video Input capture driver option.

## Important APIs, Types, And Functions
There are no C functions here. Key build semantics are the tristate symbol, prompt, dependency clauses, and selected support libraries: `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, `VIDEOBUF2_DMA_CONTIG`, and `V4L2_FWNODE`.

## Control Flow
If selected, Kbuild compiles the VIN composite object from `rcar-core.o`, `rcar-dma.o`, and `rcar-v4l2.o`. The help text states the module name is `rcar-vin`.

## State And Persistence
No runtime state exists; this file controls compile-time availability.

## Dependencies And Integration Points
The symbol depends on V4L platform drivers, OF, video device support, and Renesas architecture or compile-test. The selected options match the driver needs for media graph links, subdev APIs, DMA-contiguous vb2 buffers, and fwnode endpoint parsing.

## Risks
Any missing selected dependency would affect build or runtime media integration. Since capture buffers use contiguous DMA memory, omitting `VIDEOBUF2_DMA_CONTIG` would be a hard build break.

## Test Signals
Build with `CONFIG_VIDEO_RCAR_VIN=y` and `m`, confirm object composition and module name, and compile under `COMPILE_TEST`.
