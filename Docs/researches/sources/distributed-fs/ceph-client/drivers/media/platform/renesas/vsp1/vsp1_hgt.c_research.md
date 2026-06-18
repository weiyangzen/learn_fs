# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgt.c

Purpose: implements the VSP1 2D hue histogram generator. It configures hue-area boundaries, crop/downscale parameters, and reads fixed-size hue histogram metadata at frame end.

Important APIs and functions: `vsp1_hgt_create()`, `vsp1_hgt_frame_end()`, `hgt_hue_areas_try_ctrl()`, `hgt_hue_areas_s_ctrl()`, and `hgt_configure_stream()`. The custom `V4L2_CID_VSP1_HGT_HUE_AREAS` U8 array control holds six lower/upper hue areas.

Control flow: control validation enforces hardware ordering constraints for the 12 hue boundaries, including wrap-around behavior for area 0. Stream configuration resets HGT, writes crop offset/size, snapshots hue boundaries under the control lock, writes each area register, computes downscale ratios from crop/compose, and writes mode. Frame-end readout obtains a metadata buffer, reads max/min and sum, then reads six by 32 histogram bins.

State and persistence: `hue_areas[]` persists control state and is used for register programming. Embedded histogram state persists metadata queue and subdev state. Hardware programming is represented in display-list entries and refreshed at stream configuration.

Dependencies and integration: depends on shared histogram infrastructure, display-list writes, V4L2 controls, and HGT register definitions. Created only for feature-enabled UAPI devices.

Risks and test signals: risks include invalid hue boundary acceptance, fixed payload-size assumptions, crop/compose divide behavior, and no queued metadata buffers. Test control boundary validation, frame-end metadata capture, AHSV-only format negotiation, and selection changes.
