# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hsit.c

Purpose: implements VSP1 hue/saturation/value transform entities: HST converts ARGB to AHSV and HSI converts AHSV back to ARGB. Both are represented by the same structure with an `inverse` flag.

Important APIs and functions: `vsp1_hsit_create()`, `hsit_enum_mbus_code()`, `hsit_enum_frame_size()`, `hsit_set_format()`, and `hsit_configure_stream()`. Supported codes are ARGB8888 and AHSV8888.

Control flow: constructor picks entity type/name based on `inverse`. Enumeration reports fixed sink/source codes according to direction. Format setting only accepts sink changes, clamps dimensions, propagates to source, and swaps the media-bus code for the conversion direction. Stream configuration writes either `VI6_HSI_CTRL_EN` or `VI6_HST_CTRL_EN` into the display list.

State and persistence: persistent entity state includes `inverse`, pad formats in active subdev state, route information from common entity initialization, and pipeline membership. There is no separate runtime control state.

Dependencies and integration: depends on V4L2 subdev APIs, display-list body writes, entity helpers, and route setup in `vsp1_entity.c`. `vsp1_drv.c` creates both HSI and HST when `VSP1_HAS_HSIT` is set.

Risks and test signals: risks include incorrect direction-specific code enumeration, color-space adjustment for ARGB/AHSV, and bitwise `|` used in boolean tests. Test format negotiation on both pads, ARGB-to-AHSV and AHSV-to-ARGB graph construction, stream register traces, and media link validation.
