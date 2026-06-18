<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.c

## Purpose

`sun8i_csc.c` configures color-space conversion for DE2/DE3 mixer layers. It enables or disables YUV-to-RGB conversion and loads the proper coefficient table based on DRM framebuffer format, color encoding, color range, and channel layout.

## Important APIs, Types, And Functions

The public API is `sun8i_csc_config(struct sun8i_layer *layer, struct drm_plane_state *state)`. Internal types include `enum sun8i_csc_mode`. Important helpers are `sun8i_csc_get_mode()`, `sun8i_csc_setup()` for DE2 CCSC units, and `sun8i_de3_ccsc_setup()` for DE3 blender CSC. Coefficient tables cover limited/full range BT.601/BT.709 for DE2 and limited/full BT.601/BT.709/BT.2020 for DE3.

## Control Flow

`sun8i_csc_config()` first derives mode: off for invisible/no-CRTC/non-YUV planes, YVU2RGB for YVU formats, otherwise YUV2RGB. DE3 layers use blender CSC control bits indexed by layer channel. Older layouts pick a CCSC base from `ccsc_base[layer->cfg->ccsc][layer->channel]`. YVU modes write coefficients with U/V coefficient positions swapped; normal modes bulk-write all 12 values. Finally the CSC enable bit is updated.

## State And Persistence Behavior

There is no software state. Hardware coefficient registers and enable bits persist until the next plane update/config call or mixer reset. The function relies on current DRM plane state color encoding/range.

## Dependencies And Integration Points

It depends on DRM format/color management definitions and `sun8i_mixer` layer config/address helpers. VI/UI layer atomic update code calls it when programming YUV-capable layers.

## Risks And Test Signals

Risks include table indexing if unsupported encodings reach DE2, channel/base layout mismatch, YVU coefficient swapping errors, and stale CSC enable when planes become invisible. Test YUV and RGB formats, NV/YVU variants, full/limited and BT.601/709/2020 states, DE2/DE3/D1 CCSC layouts, plane disable, and visual color accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.c -->
