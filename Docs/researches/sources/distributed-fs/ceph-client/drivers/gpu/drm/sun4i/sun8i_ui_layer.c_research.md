# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_layer.c

## Purpose

`sun8i_ui_layer.c` implements DRM plane support for Allwinner UI layers, which handle RGB framebuffer scanout in the DE2/DE3/DE33 mixer pipeline. It validates plane state, programs layer attributes, coordinates, scaling, and DMA address registers, and creates UI planes with alpha and z-position properties.

## Important APIs, Types, and Functions

- `sun8i_ui_layer_init_one()`: allocates and initializes one `struct sun8i_layer` as a DRM universal plane.
- `sun8i_ui_layer_atomic_check()`: rejects unsupported or YUV formats and checks plane scaling constraints.
- `sun8i_ui_layer_atomic_update()`: disables invisible planes or programs attributes, coordinates, scaler, and buffer address.
- `sun8i_ui_layer_update_attributes()`: maps DRM formats to mixer hardware formats and programs alpha mode/value and enable bit.
- `sun8i_ui_layer_update_coord()`: computes source/destination sizes and fractional phases, chooses UI scaler or VI scaler on DE33, and enables/disables scaling.
- `sun8i_ui_layer_update_buffer()`: programs pitch and low DMA address for plane 0.
- `sun8i_ui_layer_formats`: supported RGB formats for UI planes.

## Control Flow

Atomic check obtains the new plane and CRTC states, validates that the framebuffer format maps to a hardware format and is not YUV, then sets min/max scale depending on `cfg->scaler_mask`. Atomic update disables the layer if the plane is not visible; otherwise it writes attributes first, then size/scaler configuration, then buffer pitch/address. Scaling is enabled when source and destination sizes differ or fractional source phases are present. DE33 UI channels reuse `sun8i_vi_scaler_setup()` and `sun8i_vi_scaler_enable()`; older DE variants use `sun8i_ui_scaler_*()`.

## State and Persistence Behavior

The DRM plane state is transient per atomic transaction; persistent layer identity lives in `struct sun8i_layer` fields initialized once: type, logical index, physical channel, overlay, regmap, and mixer configuration. Hardware registers persist until the next atomic update or disable. The file does not store shadow state beyond the DRM plane state managed by DRM helpers.

## Dependencies and Integration Points

This file depends on DRM atomic, plane, framebuffer, GEM DMA, format, blend, and probe helpers; `sun8i_mixer` for channel bases and format mapping; `sun8i_ui_scaler` for UI scaling; and `sun8i_vi_scaler` for DE33 scaling. It is called by mixer layer initialization and feeds the mixer hardware that later commits through the sunxi engine.

## Risks and Edge Cases

- `sun8i_ui_layer_update_attributes()` ignores the return value of `sun8i_mixer_drm_format_to_hw()` because atomic check should have validated it.
- Only the lower 32 bits of DMA addresses are programmed here; platforms needing high address registers require support elsewhere.
- Scaling ratios use `state->src_w / state->crtc_w` and `state->src_h / state->crtc_h`; zero or invalid dimensions should be excluded by DRM atomic checks.
- DE33's use of the VI scaler means UI and VI scaler behavior must remain compatible for RGB formats.
- Fractional phases trigger scaling even at equal integer sizes; tests should confirm visual alignment.

## Test Signals

Atomic tests should cover every advertised RGB format, alpha property behavior, no-scaling and scaling paths, fractional source offsets, invisible-plane disable, unsupported YUV rejection, and zpos limits. Hardware tests should verify pitch/address programming and scaler enable decisions on DE2/DE3/DE33.
