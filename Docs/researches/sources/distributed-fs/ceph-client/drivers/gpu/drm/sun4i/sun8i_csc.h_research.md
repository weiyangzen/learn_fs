<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.h

## Purpose

`sun8i_csc.h` declares CSC register offsets, coefficient register helpers, and the public mixer-layer CSC configuration function.

## Important APIs, Types, And Definitions

It defines CCSC base offsets for mixer0/mixer1/D1 layouts, `SUN8I_CSC_CTRL(base)`, `SUN8I_CSC_COEFF(base, i)`, and `SUN8I_CSC_CTRL_EN`. It declares `sun8i_csc_config(struct sun8i_layer *layer, struct drm_plane_state *state)`.

## Control Flow

The header has no executable control flow. Macros are consumed by `sun8i_csc.c` to address hardware coefficient and enable registers.

## State And Persistence Behavior

No software state is stored. The macros describe persistent hardware CSC registers that remain programmed across commits until changed or reset.

## Dependencies And Integration Points

It includes DRM color management declarations and forward-declares plane/layer structures. It is included by mixer/layer code that updates color conversion for YUV planes.

## Risks And Test Signals

Risks include stale offsets for SoC-specific layouts and incorrect coefficient address calculation. Compile coverage plus visual YUV playback tests on mixer0/mixer1/D1/DE3 variants validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_csc.h -->
