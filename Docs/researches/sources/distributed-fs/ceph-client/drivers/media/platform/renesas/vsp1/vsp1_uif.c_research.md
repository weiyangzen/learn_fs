# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uif.c

Purpose: implements the User Logic Interface entity, used here as a statistics/CRC window block. It exposes a V4L2 subdevice with crop selection, programs DISCOM comparison registers, and provides a function to read the current CRC.

Important APIs/functions: `vsp1_uif_create()` allocates/registers an indexed UIF as `uif.4` or `uif.5` because datasheets name instances that way. `vsp1_uif_get_crc()` reads `VI6_UIF_DISCOM_DOCMCCRCR`. `uif_get_selection()` and `uif_set_selection()` implement sink-pad crop bounds/default/current selection. `uif_configure_stream()` writes DISCOM mode, crop origin/size, and compare enable.

Control flow/state: on create, `soc_device_match()` detects r8a7796 and enables `m3w_quirk`; stream programming halves horizontal crop coordinates/sizes for that SoC. The crop rectangle is clamped to the active sink format and stored in V4L2 subdev state. There is no persistent storage.

Dependencies/integration: depends on VSP1 entity/display-list helpers, V4L2 subdev state, sys_soc matching, and VI6 UIF registers. It integrates into media graphs as a statistics entity and may be read by higher-level display validation/statistics paths.

Risks and test signals: the M3-W coordinate quirk is hardware-specific and easy to regress. Crop constraints use unsigned clamping against `format->width - 1`/`height - 1`, so valid format dimensions are assumed. Test CRC readback, crop set/get/bounds, r8a7796 horizontal coordinate behavior, and media graph routing with UIF instances.
