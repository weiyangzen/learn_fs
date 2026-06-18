<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-lb.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-lb.c

Purpose: Implements i.MX8 DC LayerBlend subdevices that combine constframe and fetchunit sources and route results toward external destinations.

Important APIs/types/functions: Exports `dc_lb_get_link_id()`, `dc_lb_pec_dynamic_prim_sel()`, `dc_lb_pec_dynamic_sec_sel()`, `dc_lb_pec_clken()`, `dc_lb_mode()`, `dc_lb_position()`, `dc_lb_get_id()`, and `dc_lb_init()`. Platform driver is `dc_lb_driver`.

Control flow: Bind maps PEC/cfg registers, creates regmaps, identifies layerblend id by MMIO base, assigns link id `LINK_ID_LAYERBLEND0 + id`, and stores it in `dc_drm->lb[]`. Init disconnects inputs, disables clock, configures shadow load/token selection for both, programs blend control, and enables shadowing. Plane update selects constframe as primary and fetchunit as secondary, enables blend mode and automatic clock, positions the blend, then points extdst at the layerblend.

State and persistence behavior: Per-layerblend state is device, regmaps, id, and link id. Register state includes input selections, clock enable, blend mode, blend factors, and position.

Dependencies: Component/platform/regmap frameworks, DRM blend alpha constants, and DC pixel-engine enums.

Integration points: Plane atomic update/disable and fetchunit disable paths call these helpers. Pixel-engine runtime resume initializes all layerblends.

Risks: Primary input choices are constrained by layerblend id; invalid selections log warnings but leave old hardware state. The blend-control setup currently uses constant alpha and zero/const blend factors tailored to the active plane path.

Test signals: Plane enable composing through expected layerblend, invalid input warning tests, runtime resume init, and visual tests for plane position/background blending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-lb.c -->
