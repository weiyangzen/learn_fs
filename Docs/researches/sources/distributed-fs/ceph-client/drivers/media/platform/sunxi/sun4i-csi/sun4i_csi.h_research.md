# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_csi.h

Purpose: central header for sun4i CSI register definitions, format descriptions, shared device state, and cross-file function declarations.

Important APIs and types: defines register offsets and bit-field helpers for enable, configuration, capture control, buffer addresses, interrupts, window size, and buffer length. It defines CSI input/output/YUV sequence enums, media pad enum `csi_subdev_pads`, `struct sun4i_csi_format`, and `struct sun4i_csi`. Exported internal APIs are `sun4i_csi_find_format`, `sun4i_csi_dma_register`, `sun4i_csi_dma_unregister`, and `sun4i_csi_v4l2_register`; subdev ops are exposed as externs.

Control flow: C files include this header to share the common device object. Core probe populates resources and media entities, DMA code consumes register constants and queue fields, and V4L2 code consumes format tables and subdev declarations.

State and persistence: `struct sun4i_csi` owns all runtime state: device resources, current double-buffer slots, scratch DMA buffer, bus config, V4L2/media/video objects, local subdev, async remote-source info, mutex/spinlock, vb2 queue, pending buffer list, and sequence counter.

Dependencies and integration points: pulls in media-device, V4L2 async/dev/fwnode, and videobuf2 core headers. It is the private ABI between `sun4i_csi.c`, `sun4i_dma.c`, and `sun4i_v4l2.c`.

Risks: register bit macros do no range checking. `CSI_MAX_WIDTH` and `CSI_MAX_HEIGHT` are broad constants, while actual traits contain lower `max_width` data that is not enforced by this header or current format paths. State fields are shared between IRQ and user paths and require correct lock discipline.

Test signals: compile coverage catches cross-file declaration drift; runtime buffer cycling validates `current_buf`, scratch, and register offset assumptions.
