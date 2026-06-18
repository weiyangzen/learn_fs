# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_iif.c

Purpose: implements the VSPX ISP Interface entity. It is an internal, three-pad processor used by VSPX-style pipelines and supports grayscale/raw-style media bus codes plus metadata.

Important APIs and functions: `vsp1_iif_create()` and `iif_configure_stream()`. Pad operations reuse generic entity handlers for code/frame-size/format enumeration and setting.

Control flow: constructor initializes an IIF entity with min/max dimensions, supported codes, three pads, and a placeholder media entity function because the entity is not exposed directly to userspace. Stream configuration writes `VI6_IIF_CTRL_CTRL` into the display list to enable/configure the block.

State and persistence: mutable state is the embedded `vsp1_entity` active subdev state, routes, media links, and pipeline membership. There are no controls or per-frame private fields. Hardware state persists through display-list programming.

Dependencies and integration: depends on `vsp1.h`, `vsp1_dl.h`, `vsp1_iif.h`, common entity pad helpers, and IIF route handling in `vsp1_entity_route_setup()` where IIF shares the BRU route with selector bits.

Risks and test signals: risks include route selector mistakes, metadata pad code handling through generic helpers, and unsupported exposure to userspace. Test VSPX pipeline construction, format propagation on all three pads, and display-list register output.
