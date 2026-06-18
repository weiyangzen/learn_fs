# sources/distributed-fs/ceph-client/include/drm/drm_bridge_connector.h

## Purpose
This small header declares the helper that creates a `drm_connector` from an encoder's bridge chain. It supports bridge-based display pipelines where the connector behavior is aggregated from bridge operations rather than implemented directly by the encoder driver.

## Important APIs, types, and functions
The only API is `drm_bridge_connector_init(struct drm_device *drm, struct drm_encoder *encoder)`, returning a connector or an error pointer/NULL depending on implementation failure mode.

## Control Flow
Drivers build and attach a bridge chain to an encoder, then call this initializer to create a connector backed by the chain's detect, modes/EDID, HPD, and HDMI/audio capabilities. The resulting connector participates in normal registration and atomic modesets.

## State and Persistence
State is owned by the connector created by the implementation. This header defines no storage, but the created connector persists until normal DRM connector cleanup and must track bridge-chain lifetime.

## Dependencies and Integration Points
It depends on `drm_bridge.h`, encoder objects, connector registration, and bridge ops. It integrates bridge-only drivers with userspace-visible connector enumeration.

## Risks and Test Signals
Risks include initializing before the bridge chain is complete, missing final bridge connector type, HPD or EDID ops not propagating, and cleanup order between connector and bridges. Tests should create fixed-panel, EDID-capable, HPD-capable, and HDMI bridge chains and verify connector properties, modes, detect status, and hot-unplug cleanup.
