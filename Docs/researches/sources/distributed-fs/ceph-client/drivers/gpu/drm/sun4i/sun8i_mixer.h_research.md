<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.h

## Purpose

`sun8i_mixer.h` defines DE2/DE3/DE33 mixer register offsets, hardware format codes, sub-engine disable registers, layer and mixer configuration structures, runtime mixer/layer state, and helper conversions used by mixer, UI/VI layer, CSC, and scaler code.

## Important APIs, Types, And Definitions

Key macros encode sizes/coordinates, global control/status/double-buffer/size registers, blender attributes/routes/modes/CSC, channel base/size for DE2/DE3/DE33, framebuffer format values for RGB/YUV/P010/P210, and unused sub-engine enable registers. Enums describe CCSC layout, mixer generation, and layer type. `struct sun8i_layer_cfg` and `struct sun8i_mixer_cfg` describe hardware capabilities. `struct sun8i_mixer` embeds `sunxi_engine`; `struct sun8i_layer` embeds `drm_plane`. Inline helpers convert plane/engine to private types and compute blender regmap/base and channel base. It declares `sun8i_mixer_drm_format_to_hw()`.

## Control Flow

The header only provides inline calculations. Runtime code uses `sun8i_blender_base()`, `sun8i_blender_regmap()`, and `sun8i_channel_base()` to choose correct addresses for DE generation and DE33 split register spaces.

## State And Persistence Behavior

Configuration structs are static per compatible; runtime structs persist for mixer and plane lifetimes. Register macros target persistent hardware state. The DE33 `map[]` translates logical DRM layer ordering to sparse physical channels.

## Dependencies And Integration Points

It includes clock/regmap/reset and DRM plane definitions plus `sunxi_engine.h`. It is included by mixer, UI/VI layer, CSC, and scaler implementations.

## Risks And Test Signals

Risks include wrong register offsets for DE generations, ambiguous format numeric values between RGB and YUV paths, scanline/scaler mask mismatches, and helper selection of wrong regmap for DE33. Test compile coverage plus runtime plane programming on DE2, DE3, DE33, D1 CCSC, RGB/YUV/P010/P210 formats, scaler availability, and route/channel mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.h -->
