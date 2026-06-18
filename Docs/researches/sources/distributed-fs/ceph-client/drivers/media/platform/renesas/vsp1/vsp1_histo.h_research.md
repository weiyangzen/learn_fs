# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_histo.h

Purpose: declares shared histogram metadata capture structures used by HGO and HGT.

Important APIs and types: defines `HISTO_PAD_SINK`, `HISTO_PAD_SOURCE`, `struct vsp1_histogram_buffer`, and `struct vsp1_histogram`. Conversion helpers are `vdev_to_histo()` and `subdev_to_histo()`. APIs include `vsp1_histogram_init()`, `vsp1_histogram_destroy()`, `vsp1_histogram_buffer_get()`, and `vsp1_histogram_buffer_complete()`.

Control flow role: HGO/HGT create their entities through `vsp1_histogram_init()`, then frame-end readers use buffer get/complete helpers. The embedded video node exposes metadata capture while the embedded `vsp1_entity` participates in the media graph.

State and persistence: queue state includes vb2 queue, IRQ queue list, wait queue, and `readout` in-progress flag. `data_size` and `meta_format` persist the ABI presented by the metadata node.

Dependencies and integration: includes Linux list/mutex/spinlock, media entity/V4L2 device/vb2, and `vsp1_entity.h`.

Risks and test signals: header changes affect both histogram implementations. Test compilation of HGO/HGT, metadata capture node registration, and streamoff with queued/readout buffers.
