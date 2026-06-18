# sources/distributed-fs/ceph-client/include/drm/drm_of.h

Purpose: declares Open Firmware/device-tree helpers for DRM display pipelines: CRTC endpoint discovery, component matching/probing, active encoder endpoints, panel/bridge lookup/removal, LVDS dual-link metadata, DSI bus lookup, and data-lane parsing.

Important APIs and types: `enum drm_lvds_dual_link_pixels` describes even/odd pixel ordering across dual LVDS links. Under `CONFIG_OF`, helpers compute CRTC masks from graph ports, find possible CRTCs, add component matches, run component probe, get an encoder's active endpoint, find a panel or bridge by port/endpoint, query LVDS pixel order at source or sink, read LVDS data mapping, and count data lanes from endpoints. Optional DSI support exposes `drm_of_get_dsi_bus()`. `drm_of_panel_bridge_remove()` finds a remote bridge and removes panel bridge wrapping when panel bridge support is enabled. Convenience helpers return active endpoint or port IDs.

Control flow: display drivers parse their DT graph during probe, derive possible CRTC routing masks, match component devices, locate downstream panels/bridges or DSI hosts, and configure LVDS/MIPI lane metadata. On teardown, panel bridge removal follows the remote endpoint and drops references.

State and persistence behavior: helper state is primarily OF node references and returned bridge/panel/host references. Stub implementations return zero or `-EINVAL` when config options are disabled. `drm_of_panel_bridge_remove()` obtains and releases OF node and bridge references within the helper.

Dependencies and integration points: depends on OF graph APIs, component framework, DRM bridge/panel, DRM encoder, MIPI DSI, LVDS bindings, and conditional `CONFIG_OF`, `CONFIG_DRM_PANEL_BRIDGE`, and `CONFIG_DRM_MIPI_DSI`.

Risks: callers must handle stubs on non-OF builds. Device-tree graph port/endpoint numbering errors propagate to wrong routing masks or missing panels. Reference handling around remote nodes and bridges must be balanced. Dual-link LVDS pixel order and lane count validation must match binding limits.

Test signals: OF and non-OF builds, componentized display pipeline probing, panel-vs-bridge lookup, DSI host lookup, active endpoint/port ID helpers, LVDS dual-link even/odd order, data-lane min/max validation, and panel bridge removal on driver unbind.
