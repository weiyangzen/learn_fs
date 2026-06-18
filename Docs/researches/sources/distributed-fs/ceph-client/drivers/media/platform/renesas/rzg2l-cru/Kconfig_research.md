<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Kconfig

Purpose: declares build options for the RZ/G2L MIPI CSI-2 receiver (`VIDEO_RZG2L_CSI2`) and Camera Receiving Unit (`VIDEO_RZG2L_CRU`).

Important APIs/types/functions: no runtime code. The two `config` symbols control whether `rzg2l-csi2` and `rzg2l-cru` modules are built. Both depend on Renesas architecture or `COMPILE_TEST`, platform V4L2 drivers, `VIDEO_DEV`, and OF. CSI-2 selects `MEDIA_CONTROLLER`, `RESET_CONTROLLER`, `V4L2_FWNODE`, and subdev API support. CRU selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, `VIDEOBUF2_DMA_CONTIG`, and subdev API support.

Control flow and state: Kconfig influences compile-time object inclusion only. There is no runtime control flow or persistence.

Dependencies and integration points: integrates the drivers into the kernel media platform driver menu. The selected dependencies match code usage: OF graph/fwnode parsing, media-controller links, reset controls, subdevice nodes, and vb2 DMA-contig for CRU capture buffers.

Risks: CSI-2 code also uses clocks, runtime PM, reset controls, and media-controller APIs; dependency coverage is mostly via selected core media symbols and normal driver framework availability. If a future code path requires DMA buffers in CSI-2 or PM beyond generic availability, Kconfig may need updates. The CRU option does not select the CSI-2 option even though the current graph path only supports CSI-2; that allows modular independent builds but requires users to enable both for complete camera pipelines.

Test signals: run `make olddefconfig` and compile with each symbol as built-in, module, and disabled; run `COMPILE_TEST` on non-Renesas architectures; verify `modinfo` names match help text (`rzg2l-csi2`, `rzg2l-cru`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Kconfig -->
