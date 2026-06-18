<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-core.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-core.c

Purpose: platform-driver and media-controller core for the RZ/G2L CRU. It allocates the device, maps variant register tables, sets up resets/clocks/IRQ/runtime PM, creates the media device, parses the OF graph, binds the external CSI-2 subdevice, and connects CSI-2, CRU IP, and CRU video entities.

Important APIs, types, and functions: `rzg2l_cru_probe()`, `rzg2l_cru_remove()`, `rzg2l_cru_media_init()`, `rzg2l_cru_mc_parse_of_graph()`, `rzg2l_cru_group_notify_*()`, and variant data `rzg2l_cru_info` / `rzg3e_cru_info`. The variant info carries max dimensions, image-converter register index, register offset table, stride support flag, IRQ handler, interrupt control callbacks, and FIFO-empty callback.

Control flow: probe maps MMIO, acquires `presetn`, `aresetn`, and `video` clock, reads OF match data, requests the variant IRQ handler, registers the CRU DMA/V4L2 core, enables runtime PM, then initializes media-controller state. The media init creates a sink pad on the video entity, fills `media_device`, sets it on `v4l2_dev`, and registers an async notifier for remote endpoint port 1. When the CSI-2 subdevice is bound and the notifier completes, CRU IP is registered, subdev nodes are created, the video node is registered, and immutable links are made from CSI-2 source pad to CRU IP sink and CRU IP source to CRU video sink.

State and persistence: device state is in `struct rzg2l_cru_dev`. Register map arrays are static const. Runtime graph binding state includes `cru->csi.asd`, `cru->csi.subdev`, `cru->ip.remote`, and media entity registration. No persistent storage.

Dependencies and integration points: platform driver, OF graph/fwnode, V4L2 async, media-controller, reset/clock/runtime PM, `rzg2l-video.c` DMA registration, and `rzg2l-ip.c` subdevice registration. OF compatibles distinguish `renesas,rzg2l-cru` and `renesas,r9a09g047-cru`.

Risks: `rzg2l_cru_media_init()` currently returns 0 even after `rzg2l_cru_mc_parse_of_graph()` reports an error, after clearing `v4l2_dev.mdev`; this can hide media graph setup failures. The group-notifier complete path does not unwind already registered IP/video entities if later link creation fails. Only CSI-2 is supported despite comments mentioning possible parallel input. Register-offset tables must stay aligned with `enum rzg2l_cru_common_regs`.

Test signals: probe both compatibles; verify reset/clock names; inspect media graph links with `media-ctl`; test disabled/missing remote endpoint handling; unbind/rebind CSI-2; compile both variants; stream through CRU to ensure the selected callbacks match the variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-core.c -->
