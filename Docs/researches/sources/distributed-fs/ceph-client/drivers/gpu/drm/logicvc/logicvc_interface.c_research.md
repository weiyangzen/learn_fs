# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_interface.c

Purpose: creates the LogiCVC output interface: encoder, optional native connector, panel, or bridge, plus panel power sequencing.

Important APIs/types/functions: `logicvc_interface_init`, `logicvc_interface_attach_crtc`, encoder helper `enable/disable`, connector `get_modes`, and mapping helpers for encoder/connector type.

Control flow: init allocates `logicvc_interface`, discovers panel or bridge through `drm_of_find_panel_or_bridge`, initializes encoder type from configured display interface, optionally initializes a connector for native DVI or panel-backed outputs, attaches connector to encoder, and attaches bridge if present. Encoder enable turns on `LOGICVC_POWER_CTRL_VIDEO_ENABLE` and prepares/enables panel; disable reverses panel state.

State and persistence: stores encoder, connector, and panel/bridge pointers in `logicvc->interface`. Hardware video power bit remains set until disabled or reset.

Dependencies and integration points: depends on DRM OF, panel, bridge, connector, encoder, and probe helper APIs; consumes display interface config from `logicvc_drm.h`; attaches to the CRTC after CRTC creation.

Risks and test signals: native DVI mode probing is not implemented, so native connector without panel returns no modes. Panel/bridge probe deferral must be propagated. Test RGB/LVDS/DVI configs, panel get_modes, bridge attach, and encoder enable/disable.
