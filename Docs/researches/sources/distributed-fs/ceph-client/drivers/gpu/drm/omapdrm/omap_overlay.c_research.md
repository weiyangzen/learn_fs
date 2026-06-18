# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_overlay.c

Purpose: Owns allocation and lifecycle of OMAP hardware overlays and their assignment to DRM planes during atomic state validation.

Important APIs/types/functions: `omap_hwoverlays_init`, `omap_hwoverlays_destroy`, `omap_overlay_assign`, `omap_overlay_release`, and `omap_overlay_update_state`. Internal helpers map overlay IDs to names, find a free overlay with required caps and fourcc support, allocate overlay records, and free them.

Control flow: Initialization queries DISPC overlay count and capabilities and stores `struct omap_hw_overlay` entries in `priv->overlays`. During atomic check, planes call `omap_overlay_assign` against the transaction-global `hwoverlay_to_plane` map; dual-overlay planes request a second overlay and roll back on failure. Release clears the same global map. Atomic update/disable calls `omap_overlay_update_state` on previously held overlays, disabling hardware overlays no longer present in the committed global state.

State and persistence: Persistent state is `priv->overlays[]` and `priv->num_ovls`; per-transaction state is `omap_global_state->hwoverlay_to_plane`.

Dependencies and integration: Depends on DISPC overlay capability and format queries, OMAP global atomic state, and `omap_plane.c` for assignment/release calls.

Risks: Hardware overlay allocation is first-fit and can fail due to transaction ordering when formats/caps are constrained. Dual-overlay assignment must keep z-order and right/left split consistent with plane update logic. `omap_overlay_update_state` assumes a valid existing global state.

Test signals: Atomic commits with scaling, format changes, invisible planes, dual-wide planes, caps mismatch, and overlay exhaustion. Confirm disabled old overlays are turned off after reassignment.
