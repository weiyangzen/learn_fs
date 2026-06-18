# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_connector.h

Purpose: Declares Nouveau connector state, connector atom properties, helper macros, backlight hooks, and connector public APIs.

Important APIs/types: `struct nouveau_conn_atom` extends `drm_connector_state` with dithering, scaler/underscan, procamp, and a bitmask of changed property groups. `struct nouveau_connector` wraps `drm_connector` and stores DCB type/index, nvif connector and hotplug/IRQ events, DP AUX, fixed DP encoder, detected encoder, EDID, native mode, optional backlight, and non-atomic property state. Helpers include `nouveau_connector()`, `nouveau_connector_is_mst()`, `nouveau_for_each_non_mst_connector_iter`, and `nouveau_crtc_connector_get()`.

Control flow/state contract: Atomic paths allocate and duplicate `nouveau_conn_atom`; legacy pre-NV50 paths use the embedded `properties_state`. Connector code uses MST filtering for iteration, and `nouveau_crtc_connector_get()` maps a CRTC to its active non-MST connector.

Dependencies/integration: Includes nvif conn/event, NV display class definitions for property enum values, DRM DP/CRTC/encoder utilities, and Nouveau CRTC/encoder declarations. Backlight APIs compile to no-ops when `CONFIG_DRM_NOUVEAU_BACKLIGHT` is disabled.

Risks/test signals: The dither enum values intentionally match hardware fields, so changing them can break nv50/gf119 programming. Connector iteration excludes MST connectors by design. Test build variants with and without backlight/debug configs, property propagation into atomic state, MST connector filtering, and CRTC-to-connector lookup under cloned or disconnected modes.
