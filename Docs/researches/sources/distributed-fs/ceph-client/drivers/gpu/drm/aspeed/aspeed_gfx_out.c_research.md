## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_out.c

Purpose: creates the single ASPEED GFX connector and supplies fallback modes without EDID.

Important functions are `aspeed_gfx_get_modes` and `aspeed_gfx_create_output`, plus connector helper/func tables. The connector type is `DRM_MODE_CONNECTOR_Unknown`; it uses atomic connector state helpers and `drm_helper_probe_single_connector_modes`.

Control flow: output creation initializes connector fields, attaches helpers, and calls `drm_connector_init`. Mode probing always adds no-EDID modes up to 800x600. State is the embedded connector in `struct aspeed_gfx`; there is no hotplug or EDID persistence. Dependencies are DRM connector, EDID/no-EDID helpers, and the simple display pipe that attaches to this connector.

Risks include no physical detect, no EDID, no preferred mode assignment, and a connector initialized with `dpms = OFF` but no explicit detect path. Test signals are connector creation during probe, userspace seeing 800x600 modes, successful atomic state reset/duplicate/destroy, and pipe initialization attaching this connector.
