# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_sru.h

Purpose: declares the SRU subdevice structure and constructor for the VSP1 Super Resolution Unit.

Important APIs/types: defines `SRU_PAD_SINK` and `SRU_PAD_SOURCE`, `struct vsp1_sru` with embedded `vsp1_entity`, V4L2 control handler, and current `intensity`, `to_sru()` for container conversion, and `vsp1_sru_create()`.

Control flow/state: state is runtime-only and stored in the subdevice state plus the integer intensity control. No persistence is defined.

Dependencies/integration: included by SRU implementation and any VSP1 device initialization code that creates optional SRU hardware. It depends on media entity, V4L2 controls/subdev, and `vsp1_entity.h`.

Risks and test signals: header changes affect entity initialization and control access. Compile-test configurations with and without SRU support and exercise control setup/cleanup.
