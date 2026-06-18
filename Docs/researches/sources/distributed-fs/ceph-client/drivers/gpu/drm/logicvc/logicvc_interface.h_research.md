# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_interface.h

Purpose: declares LogiCVC output-interface state and setup helpers.

Important APIs/types/functions: `struct logicvc_interface` embeds a DRM encoder and connector and stores optional `drm_panel`/`drm_bridge`. Exports `logicvc_interface_init` and `logicvc_interface_attach_crtc`.

Control flow: core probe calls init, then attach after CRTC setup.

State and persistence: interface object persists for DRM device lifetime under devm allocation. It is the output endpoint for atomic modesets.

Dependencies and integration points: includes DRM bridge, connector, encoder, and panel headers. Consumed by CRTC for bus flags and by mode/probe setup.

Risks and test signals: assumes one output interface per device. Test with bridge-only, panel connector, and native connector paths.
