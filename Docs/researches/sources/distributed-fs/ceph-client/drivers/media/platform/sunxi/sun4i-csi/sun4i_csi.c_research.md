# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_csi.c

Purpose: implements the platform-driver, resource, media-device, async-notifier, and runtime-PM backbone for the sun4i/sun7i CSI capture driver.

Important APIs and functions: module entry is `module_platform_driver(sun4i_csi_driver)`. Main lifecycle functions are `sun4i_csi_probe`, `sun4i_csi_remove`, `sun4i_csi_runtime_resume`, and `sun4i_csi_runtime_suspend`. Async media callbacks are `sun4i_csi_notify_bound` and `sun4i_csi_notify_complete`. Local trait data is held in `struct sun4i_csi_traits` and selected by `sun4i_csi_of_match`.

Control flow: probe allocates `struct sun4i_csi`, maps registers, gets IRQ, clocks, and reset, initializes a media device and local CSI subdevice, initializes media pads for the subdevice and video node, registers the DMA/V4L2 base through `sun4i_csi_dma_register`, parses the fwnode endpoint, registers a V4L2 async notifier, then enables runtime PM. When a remote sensor subdevice binds, the driver finds the source pad and stores the parallel bus configuration. Notifier completion registers the local subdevice, registers the video device, registers the media device, creates immutable source-to-CSI and CSI-to-video links, and registers subdevice devnodes. Runtime resume deasserts reset, enables bus/RAM/optional ISP clocks, and writes `CSI_EN_REG`; suspend disables clocks and asserts reset.

State and persistence: persistent driver state is in `struct sun4i_csi`, including MMIO base, clocks, reset, traits, media/V4L2/video/subdev objects, bus configuration, notifier, and buffer queue state initialized by the DMA file. Hardware register state is volatile and rebuilt on stream start or runtime resume.

Dependencies and integration points: depends on platform resources, device tree compatibles `allwinner,sun4i-a10-csi1` and `allwinner,sun7i-a20-csi0`, V4L2 async/fwnode APIs, media-controller links, videobuf2 DMA-contig, common clock, reset, and runtime PM. It delegates capture queue setup to `sun4i_csi_dma_register` and video node setup to `sun4i_csi_v4l2_register`.

Risks: `clk_set_rate` and `clk_prepare_enable` are called on `isp_clk` even for traits without ISP; nullable clock handling depends on the clock API tolerating NULL pointers. Error paths after notifier completion can leave already registered entities if later steps fail. Link validation for the video entity only warns once and always succeeds.

Test signals: platform probe/remove on A10/A20 device-tree nodes, media graph link creation with a remote sensor, runtime suspend/resume, module unload, and streaming smoke tests covering both `has_isp` false and true traits.
