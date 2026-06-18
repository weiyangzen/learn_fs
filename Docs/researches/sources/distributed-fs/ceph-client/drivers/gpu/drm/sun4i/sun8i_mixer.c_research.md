<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.c

## Purpose

`sun8i_mixer.c` implements the DE2/DE3/DE33 display mixer as a `sunxi_engine`. It maps DRM formats to hardware formats, creates VI/UI planes, commits blender routing/coordinates/z-order, programs output size/interlace mode, resets and initializes mixer registers, and binds mixer instances into the sun4i DRM engine list.

## Important APIs, Types, And Functions

The exported format helper is `sun8i_mixer_drm_format_to_hw()`. Engine ops are `sun8i_mixer_commit()`, `sun8i_layers_init()`, and `sun8i_mixer_mode_set()`. Lifecycle helpers are `sun8i_mixer_of_get_id()`, `sun8i_mixer_init()`, `sun8i_mixer_bind()`, and `sun8i_mixer_unbind()`. Variant config tables describe VI/UI counts, scaler masks, CCSC layout, DE generation, scanline limits, module clock rate, and DE33 channel map.

## Control Flow

Bind enforces a 32-bit DMA mask, allocates mixer/engine state, optionally sets the DRM DMA device, derives an engine id from OF endpoint, maps main and for DE33 top/display regmaps, deasserts reset, enables bus/mod clocks and optional fixed mod rate, adds the engine to `drv->engine_list`, clears DE2/DE3 register ranges, disables unused sub-engines, then initializes blender defaults. Plane initialization creates VI planes first, then UI planes, assigning primary role based on available channels and DE33 physical channel mapping. Commit scans DRM planes for the target CRTC, routes enabled layers to blender pipes by normalized zpos, writes pipe coordinates and sizes, then updates route/pipe-enable and double-buffer control. Mode set updates global/blender output size and interlace bit.

## State And Persistence Behavior

Persistent state is `struct sun8i_mixer`, embedded `sunxi_engine`, regmaps, clocks, reset, and variant config. Hardware state persists in global, channel, blender, sub-engine, double-buffer, route, and size registers until next commit/mode-set/reset. DRM plane state controls visible layers and zpos.

## Dependencies And Integration Points

It depends on DRM atomic/plane helpers, DMA mask APIs, component framework, OF graph, clocks/resets/regmap, `sun8i_ui_layer`, `sun8i_vi_layer`, CSC/scaler code via layer updates, and TCON engine matching through `drv->engine_list`.

## Risks And Test Signals

Risks include 32-bit DMA limitations, CRTC id fallback for old DTs, DE33 split regmap/channel map handling, clearing guessed register ranges, route/zpos correctness, disabled sub-engine assumptions, and fixed mod-clock requirements. Test all compatible mixer configs, VI/UI plane creation, YUV/RGB formats, zpos routing, interlace output, DE33 H616 mapping, high DMA addresses, and repeated commits with disabled planes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_mixer.c -->
