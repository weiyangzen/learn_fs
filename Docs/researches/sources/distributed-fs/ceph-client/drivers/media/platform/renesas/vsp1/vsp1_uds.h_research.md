# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uds.h

Purpose: declares the VSP1 UDS entity interface.

Important APIs/types: defines `UDS_PAD_SINK` and `UDS_PAD_SOURCE`, `struct vsp1_uds` with embedded `vsp1_entity` and `scale_alpha` flag, `to_uds()` conversion helper, `vsp1_uds_create()`, and `vsp1_uds_set_alpha()`.

Control flow/state: `scale_alpha` is set by pipeline setup from upstream alpha availability and influences stream programming. The rest of state lives in V4L2 subdevice pad formats.

Dependencies/integration: included by `vsp1_uds.c`, `vsp1_pipe.c`, and `vsp1_video.c`. It needs media entity/subdev definitions and `vsp1_entity.h`.

Risks and test signals: API risk is mainly around `scale_alpha` semantics and alpha propagation from RPF/BRx. Test UDS pipelines with alpha formats and with BRU/BRS before UDS.
