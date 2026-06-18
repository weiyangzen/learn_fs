# sources/distributed-fs/ceph-client/include/drm/drm_connector.h

## Purpose
This header defines DRM connector types, sink capability structures, mutable connector atomic state, connector callback tables, HDMI/audio/CEC helpers, command-line mode representation, the central `drm_connector` object, connector property APIs, tile groups, and safe connector-list iteration. It is the main contract for display outputs exposed to userspace.

## Important APIs, types, and functions
Important enums include connector force/status/registration state, TV modes, link status, panel orientation, HDMI broadcast RGB, privacy-screen status, colorspace, output color format, and bus flags. Key structs include `drm_display_info`, HDMI/SCDC/DSC capability structs, TV and HDMI connector state, `drm_connector_state`, HDMI audio/infoframe/CEC function tables, `drm_connector_funcs`, `drm_cmdline_mode`, `drm_connector_hdmi_audio`, `drm_connector_hdmi`, `drm_connector_cec`, `drm_connector`, `drm_tile_group`, and `drm_connector_list_iter`. APIs initialize/register/unregister/cleanup connectors, attach encoders and properties, update EDID/link/VRR/tile/path/privacy/orientation state, create tile groups, iterate connectors safely, and map enum values to names.

## Control Flow
Drivers initialize connectors with function tables and optional DDC/HDMI metadata, attach possible encoders, register connectors to userspace, probe modes through `fill_modes`/detect/EDID helpers, and update properties as hotplug or EDID data changes. Atomic transactions duplicate connector state, set standardized or private properties, select best encoders, route connectors to CRTCs, validate HDMI infoframes/audio/HDR, and commit state. Safe iteration uses `drm_connector_list_iter` because connectors may be hot-added or removed.

## State and Persistence
`struct drm_connector` persists as a refcounted mode object with sysfs/debugfs presence, registration state, mode lists, EDID blob, properties, display info, possible encoders, current legacy encoder, ELD/audio latency, DDC adapter, EDID error counters, tile data, HDMI audio/infoframe state, and CEC data. `drm_connector_state` is mutable atomic state containing CRTC routing, best encoder, link status, TV settings, content/scaling/protection/color/HDR/privacy/max-bpc/writeback/HDMI state. Locks include connector mutex, mode-config mutexes, ELD mutex, EDID override mutex, HDMI infoframe/audio mutexes, and CEC mutex.

## Dependencies and Integration Points
It depends on DRM mode objects, properties, UAPI modes, EDID parsing, HDMI infoframes, I2C DDC, panels, privacy screens, writeback jobs, CEC, platform devices, fwnode, notifier blocks, and encoders/CRTCs. It integrates userspace GETCONNECTOR/atomic properties, hotplug polling, fb helpers, bridge connectors, HDMI codec framework, DP MST tiling, panel orientation quirks, and content protection.

## Risks and Test Signals
Risks include using unregistered connectors in modesets, stale connector references outside list iteration, inconsistent EDID/display_info updates, property creation not matching state fields, HDMI infoframe/audio races with ALSA, privacy-screen notifier races, tile/path blob lifetime bugs, bad max-bpc/colorspace validation, and legacy versus atomic DPMS confusion. Tests should cover hotplug add/remove, registration-state restrictions, connector lookup refcounts and leases, EDID update and corrupt/null counters, command-line forced modes, property attach/set/get paths, HDMI init/infoframe/audio callbacks, CEC physical address updates, tile group refcounts, privacy-screen provider updates, connector-list iteration during removal, and atomic state duplicate/destroy with HDR/writeback blobs.
