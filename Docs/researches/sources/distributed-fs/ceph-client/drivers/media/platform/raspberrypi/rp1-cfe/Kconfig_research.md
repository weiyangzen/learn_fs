# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/Kconfig

Purpose: defines the Kconfig symbol for Raspberry Pi RP1 Camera Front End capture support.

Important APIs/types/functions: `config VIDEO_RP1_CFE` is tristate, depends on `VIDEO_DEV` and `PM`, and selects `VIDEO_V4L2_SUBDEV_API`, `MEDIA_CONTROLLER`, `VIDEOBUF2_DMA_CONTIG`, and `V4L2_FWNODE`.

Control flow: selecting the symbol builds the composite `rp1-cfe` driver.

State and persistence: kernel configuration only.

Dependencies and integration: selected dependencies match the driver use of async fwnode subdev binding, media-controller graph links, V4L2 subdev streams/routing, runtime PM, and DMA-contiguous vb2 queues.

Risks: no architecture dependency is present here, so compile coverage is broad; runtime binding still depends on a matching `raspberrypi,rp1-cfe` device tree node and resources.

Test signals: compile as built-in/module, config dependency resolution, and device-tree probe on RP1 hardware with sensor endpoint.
