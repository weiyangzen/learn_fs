# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_of.c

## Purpose
This file contains DRM Device Tree helper functions for graph-based display pipelines. It maps OF graph ports to CRTCs, builds component framework matches, finds active encoder endpoints, locates connected panels or bridges, decodes dual-link LVDS metadata, counts DSI/eDP data lanes, and locates the DSI host for non-DSI-controlled display devices.

## Important APIs, Types, and Functions
CRTC/encoder graph helpers are `drm_of_crtc_port_mask()`, `drm_of_find_possible_crtcs()`, `drm_of_component_match_add()`, `drm_of_component_probe()`, and `drm_of_encoder_active_endpoint()`. Panel/bridge lookup is `drm_of_find_panel_or_bridge()`. LVDS helpers are `drm_of_lvds_get_dual_link_pixel_order()`, `drm_of_lvds_get_dual_link_pixel_order_sink()`, and `drm_of_lvds_get_data_mapping()`. Lane helpers are `drm_of_get_data_lanes_count()` and `drm_of_get_data_lanes_count_ep()`. When MIPI DSI support is enabled, `drm_of_get_dsi_bus()` returns a `mipi_dsi_host` for a device's input graph.

## Control Flow
`drm_of_find_possible_crtcs()` walks endpoints of an encoder port, follows each remote port, and ORs the matching CRTC bit from `drm_of_crtc_port_mask()`. `drm_of_component_probe()` first adds CRTC ports listed in the master's `ports` phandle property, then adds remote encoder-side components reachable from those ports, and finally calls `component_master_add_with_match()`. This ordering lets encoder bind callbacks query possible CRTCs.

Panel/bridge lookup first validates that a graph exists, obtains the requested remote node, tries panel lookup, then bridge lookup if no panel was found. LVDS source pixel order follows remote sink port properties and verifies both links form an even/odd pair; sink pixel order reads the sink ports directly. Data lane helpers count `data-lanes` elements and validate min/max bounds. `drm_of_get_dsi_bus()` follows device `port@0` to the remote DSI host node and returns `-EPROBE_DEFER` until the host is registered.

## State and Persistence Behavior
The helpers do not maintain global state. They acquire and release OF node references around graph traversal and component match setup. `drm_of_component_match_add()` intentionally takes an OF reference and registers `component_release_of` so the component framework owns release. Results are transient masks, pointers, or media bus format constants; persistent ownership remains with the DRM device, OF core, component framework, DSI host registry, panel subsystem, or bridge subsystem.

## Dependencies and Integration Points
The file depends on Linux OF graph APIs, component framework, media bus format constants, DRM CRTC/encoder/bridge/panel APIs, and MIPI DSI host lookup when enabled. It is used by Device Tree based display drivers to wire encoders to CRTCs, bind multi-component display devices, discover downstream panels/bridges, configure LVDS bus mapping, validate link lane count, and defer probing until DSI hosts are ready.

## Risks
Graph parsing is reference-sensitive; missing `of_node_put()` calls would leak nodes, while premature puts can invalidate comparisons. `drm_of_find_possible_crtcs()` returns 0 immediately if any endpoint lacks a remote port, which can hide other valid endpoints. `drm_of_component_probe()` requires a `ports` phandle property and available parent devices; malformed or disabled nodes fail binding. `drm_of_find_panel_or_bridge()` is deprecated for new drivers in favor of managed bridge lookup. LVDS helpers enforce all remote endpoints on a port having the same pixel type, which may reject more complex topologies. `drm_of_get_dsi_bus()` assumes `port@0` is the DSI input.

## Test Signals
Signals include DT graph unit tests or board boots where possible CRTC masks match expected ports, component master binding orders CRTCs before encoders, active encoder endpoint parsing matches the connected CRTC, panel/bridge lookup returns the expected downstream object or defers cleanly, LVDS even/odd ordering and data mapping strings produce correct media bus formats, invalid dual-link properties return `-EINVAL` or `-EPIPE`, data-lane counts enforce min/max bounds, and DSI bus lookup defers until host registration then succeeds.
