<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru.h

Purpose: shared private header for the RZ/G2L CRU composite driver. It defines device structures, format descriptors, DMA state, limits, and cross-file function prototypes used by `rzg2l-core.c`, `rzg2l-ip.c`, and `rzg2l-video.c`.

Important APIs/types/functions: `struct rzg2l_cru_dev` is the central state object, holding MMIO base, variant info, reset/clock handles, video and V4L2 devices, async notifiers, CRU IP/CSI/media graph state, vb2 queue, scratch DMA buffer, hardware buffer slots, queued buffers, sequence, DMA state, and active V4L2 format. `struct rzg2l_cru_info` abstracts variant max dimensions, register map, stride support, IRQ and interrupt callbacks, and FIFO-empty callback. `struct rzg2l_cru_ip_format` connects media-bus codes, CSI-2 datatypes, V4L2 pixel formats, `ICnDMR`, and YUV/raw classification.

Control flow and state: no executable flow, but the header defines the state machine values `STOPPED`, `STARTING`, `RUNNING`, and `STOPPING`. The prototypes show module boundaries: core handles platform/media setup, IP handles subdev format/stream handoff, and video handles DMA, IRQs, vb2, and video-node ioctls.

Dependencies and integration points: includes V4L2 async/dev/device and vb2-v4l2 headers plus reset and IRQ types. It is private to this driver directory and not a UAPI. The fixed hardware buffer counts and alignment mask are consumed by DMA slot management.

Risks: `buf_addr` is sized to `RZG2L_CRU_HW_BUFFER_DEFAULT` while `queue_buf` is sized to `RZG2L_CRU_HW_BUFFER_MAX`; current code sets `num_buf` to the default, but raising `num_buf` would overflow `buf_addr`. Function pointer contracts in `rzg2l_cru_info` must match variant register availability. The `enum rzg2l_csi2_pads` name actually describes CRU IP pads, which may confuse future edits.

Test signals: build all CRU objects together; run sparse or Coccinelle for prototype drift; test variant callbacks and hardware slot limits; audit any future change to `num_buf`, pad enum names, or `struct rzg2l_cru_dev` locking fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru.h -->
