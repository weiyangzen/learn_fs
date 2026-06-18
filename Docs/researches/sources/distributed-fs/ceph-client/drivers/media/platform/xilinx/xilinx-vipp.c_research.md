# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vipp.c

Purpose: platform driver for the top-level Xilinx video composite device (`xlnx,video`). It creates the media device and V4L2 device, initializes DMA endpoints described by child port nodes, discovers all connected subdevices through the firmware graph, and creates media links when async binding completes.

Important types/APIs: `struct xvip_graph_entity` extends `v4l2_async_connection` with entity/subdev pointers. Key routines are graph parsing (`xvip_graph_parse_one`, `xvip_graph_parse`), DMA setup (`xvip_graph_dma_init_one/init`), link building (`xvip_graph_build_one`, `xvip_graph_build_dma`), notifier callbacks, composite V4L2/media init/cleanup, probe, and remove.

Control flow: probe allocates `xvip_composite_device`, initializes media/V4L2 devices, then calls graph init. DMA init scans `ports` children, reads `direction` and `reg`, creates capture or output `xvip_dma` nodes, and records capabilities. Graph parsing starts from the composite node and recursively adds remote subdevice fwnodes, skipping the composite itself. When all subdevices bind, the notifier builds subdev-to-subdev links from source pads, builds DMA-to-subdev links for composite endpoints, registers subdev nodes, and registers the media device.

State and persistence: runtime state is the V4L2/media device, async notifier lists, and list of DMA endpoints. No persistent state. DMA devices remain in `xdev->dmas` until cleanup.

Dependencies and integration: relies on OF graph/fwnode links, V4L2 async notifier, media-controller APIs, `xilinx-dma`, and child subdevice drivers such as TPG and CSI-2. Compatible is `xlnx,video`.

Risks: `xvip_graph_parse()` returns success when parsing the top-level graph fails, which can mask malformed graph failures until later empty/notifier checks. Link creation assumes firmware port numbers map to media pad indexes. DMA direction strings are inverted to V4L2 buffer type semantics and must match DT convention. Test signals include DT graph parsing with multiple subdevices, async bind completion, media topology inspection, DMA link direction validation, and cleanup after partial probe failure.
