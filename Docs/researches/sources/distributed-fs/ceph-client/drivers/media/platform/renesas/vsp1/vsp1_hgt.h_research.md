# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgt.h

Purpose: declares the 2D histogram generator private structure and public local functions.

Important APIs and types: defines `HGT_NUM_HUE_AREAS` as six, `struct vsp1_hgt` with embedded `vsp1_histogram`, V4L2 control handler, and 12-byte hue boundary cache. `to_hgt()`, `vsp1_hgt_create()`, and `vsp1_hgt_frame_end()` are the conversion, constructor, and frame-end readout APIs.

Control flow role: `vsp1_drv.c` creates HGT when supported, and pipeline frame-end code uses `vsp1_hgt_frame_end()` to complete metadata buffers. `vsp1_hgt.c` owns all control validation and register programming.

State and persistence: hue areas persist in `hue_areas[]`; queue/readout state persists in the embedded histogram object.

Dependencies and integration: includes media/V4L2 control/subdev headers and shared `vsp1_histo.h`.

Risks and test signals: if `HGT_NUM_HUE_AREAS` or structure layout changes, both control dimensions and register programming must change. Test hue-area controls and metadata output size.
