# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_iif.h

Purpose: declares the VSPX ISP Interface entity wrapper and pad indexes.

Important APIs and types: defines `VSPX_IIF_SINK_PAD_IMG`, `VSPX_IIF_SINK_PAD_CONFIG`, `struct vsp1_iif`, `to_iif()`, and `vsp1_iif_create()`. The structure only embeds `struct vsp1_entity`.

Control flow role: used by `vsp1_drv.c` to instantiate IIF on VSPX Gen4 variants and by VSPX/IIF configuration code to access the entity.

State and persistence: all state is inherited from the embedded entity: pad formats, media links, route, and pipeline membership.

Dependencies and integration: includes V4L2 subdev and common entity declarations.

Risks and test signals: pad constants must stay aligned with the hardware and with any VSPX code that references image versus config inputs. Test VSPX graph/pipeline setup and compile coverage for IIF-enabled builds.
