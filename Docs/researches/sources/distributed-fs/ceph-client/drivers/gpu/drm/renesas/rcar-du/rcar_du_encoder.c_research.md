# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_encoder.c

## Purpose

`rcar_du_encoder.c` creates DRM encoders and bridge connectors for DU output routes described by device tree. It handles direct DPAD panels, generic bridges, LVDS/DSI bridge bookkeeping, Gen3 LVDS dual-link/connection filtering, and connector attachment.

## Important APIs, Types, and Functions

- `rcar_du_encoder_count_ports()` counts `port` children under a node or the node itself.
- `rcar_du_encoder_init()` resolves a panel or bridge for one output, allocates `struct rcar_du_encoder`, attaches the bridge without a connector, creates a bridge connector, and attaches it to the encoder.
- `rcar_du_encoder_funcs` is currently empty, relying on DRM managed cleanup/default behavior.

## Control Flow

For DPAD outputs with a single port, the node is treated as a panel and wrapped with a panel bridge. Other outputs locate an existing DRM bridge from the DT node and store LVDS/DSI bridge pointers in the DU device for later pixel-clock control. Gen3 skips LVDS1 when it is a companion in dual-link mode and skips disconnected LVDS outputs. Finally, a managed DRM encoder is allocated, the bridge chain is attached, a connector is created from the bridge chain, and the connector is attached to the encoder.

## State and Persistence Behavior

Persistent state includes the managed `struct rcar_du_encoder` and its output enum. DU device state may store bridge pointers in `rcdu->lvds[]` or `rcdu->dsi[]`. DRM connector/encoder/bridge attachments persist for the DRM device lifetime.

## Dependencies and Integration Points

- Uses OF graph/device nodes, DRM bridge, bridge connector, panel bridge, and local LVDS helpers.
- Called by `rcar_du_kms.c` while iterating endpoints from DT route tables.

## Risks and Edge Cases

- `of_drm_find_bridge()` returning NULL is treated as probe deferral, so absent bridges can defer the whole DU if DT indicates they should exist.
- DPAD single-port heuristic assumes such nodes describe panels; unusual bridge DT layouts could be misclassified.
- Gen3 LVDS filtering depends on `rcar_lvds_dual_link()` and `rcar_lvds_is_connected()` matching hardware topology.

## Test Signals

- DT tests should cover DPAD panel bridge, external bridges, HDMI/LVDS/DSI outputs, disconnected LVDS, and dual-link LVDS companion behavior.
- Connector enumeration should show exactly one connector per usable output pipeline.
