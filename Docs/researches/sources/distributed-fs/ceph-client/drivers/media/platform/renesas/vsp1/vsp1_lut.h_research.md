# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lut.h

Purpose: declares private state for the VSP1 1D LUT entity.

Important APIs and types: defines `LUT_PAD_SINK`, `LUT_PAD_SOURCE`, `struct vsp1_lut`, `to_lut()`, and `vsp1_lut_create()`. The structure embeds the common entity, a V4L2 control handler, spinlock, pending LUT display-list body, and body pool.

Control flow role: entity creation and subdev callbacks convert from `v4l2_subdev` to `vsp1_lut` with `to_lut()`. The pending body and pool fields are used to hand table updates from control context to frame configuration.

State and persistence: control state is handled by the V4L2 control core; pending table programming persists in `lut` until consumed. The body pool owns DMA memory for table register writes.

Dependencies and integration: includes spinlock, media entity, V4L2 controls/subdev, and common entity declarations.

Risks and test signals: changes must preserve lock-protected table handoff. Test LUT control updates, stream configuration, and entity cleanup.
