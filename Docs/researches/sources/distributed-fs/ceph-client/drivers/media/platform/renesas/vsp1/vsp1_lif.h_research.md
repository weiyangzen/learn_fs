# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lif.h

Purpose: declares the LIF entity wrapper used by DRM display pipelines.

Important APIs and types: defines `LIF_PAD_SINK`, `LIF_PAD_SOURCE`, `struct vsp1_lif`, `to_lif()`, and `vsp1_lif_create()`. `struct vsp1_lif` embeds only the common `vsp1_entity`.

Control flow role: `vsp1_drv.c` creates LIF entities only for non-UAPI display use. `vsp1_drm.c` attaches each pipeline's WPF to its LIF and calls subdev pad operations before entity stream configuration.

State and persistence: all mutable state is held by the embedded entity and its active subdev state.

Dependencies and integration: includes media entity/V4L2 subdev and common entity declarations.

Risks and test signals: LIF index and pad constants must match DRM setup. Test all LIF counts declared in `vsp1_device_info` and dual-pipeline devices.
