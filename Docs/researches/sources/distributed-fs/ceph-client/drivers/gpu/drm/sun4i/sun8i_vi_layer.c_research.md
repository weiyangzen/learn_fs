# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_vi_layer.c

## Purpose

`sun8i_vi_layer.c` implements DRM plane support for Allwinner VI layers, which handle RGB and YUV/video framebuffer scanout. It validates plane formats and scaling, programs attributes, chroma-aware dimensions and phases, scaler/coarse-scaler state, CSC configuration, DMA addresses for multi-plane formats, alpha/color properties, and z-order.

## Important APIs, Types, and Functions

- `sun8i_vi_layer_init_one()`: allocates and registers a VI plane with format list, optional alpha, zpos, and color encoding/range properties.
- `sun8i_vi_layer_atomic_check()`: validates hardware format support and scaling constraints.
- `sun8i_vi_layer_atomic_update()`: disables invisible planes or programs attributes, coordinate/scaler state, CSC, and DMA buffers.
- `sun8i_vi_layer_update_coord()`: aligns source geometry for chroma subsampling, decides whether scaling is required, computes coarse downscaling, and sets VI scaler registers.
- `sun8i_vi_layer_update_attributes()`: writes format, RGB/YUV mode, enable, and alpha/global alpha fields.
- `sun8i_vi_layer_update_buffer()`: writes pitch and low DMA address for each framebuffer plane.
- `sun8i_vi_layer_formats` and `sun8i_vi_layer_de3_formats`: supported format sets for DE2 versus DE3+.

## Control Flow

Atomic check obtains the new plane and CRTC states, validates format mapping, then allows scaling only for channels present in `cfg->scaler_mask`. Atomic update disables if not visible; otherwise it writes attributes, coordinate/scaler state, CSC, and buffer addresses. Coordinate update derives integer sizes and fractional phases from DRM source/destination rectangles. For subsampled formats, it rounds source offsets and sizes to chroma alignment and folds the remainder into phase. Scaling is required for size changes, subsampling, or fractional phase. When scaling is active, the function estimates VI scaler vertical ability from mixer module clock, frame rate, display height, and max source/destination width; if insufficient, it enables vertical coarse downscaling. It also coarse-downscales horizontally when the source width exceeds the channel scanline limit. Fine scaling is then programmed through `sun8i_vi_scaler_setup()`, and coarse ratios are written to HDS/VDS registers.

## State and Persistence Behavior

Persistent software state lives in the allocated `struct sun8i_layer` and DRM plane properties. Hardware state includes VI layer attribute/size/pitch/address registers, scaler state, coarse downscale registers, and CSC registers. The implementation resets coarse downscale values to zero when not needed by writing all four HDS/VDS registers each update.

## Dependencies and Integration Points

This file depends on DRM atomic, blend, color, framebuffer, GEM DMA, and plane helpers; `sun4i_crtc` and `sunxi_engine` to reach the mixer clock; `sun8i_mixer` for channel base and format mapping; `sun8i_csc` for color conversion; and `sun8i_vi_scaler` for fine scaling. It integrates with DRM color encoding/range properties and mixer configuration quirks such as `de2_fcc_alpha`, `scanline_yuv`, and `de_type`.

## Risks and Edge Cases

- Format mapping is trusted in update after atomic check.
- DMA high-address registers are not programmed in this file; addresses above 32 bits require support elsewhere or suitable DMA constraints.
- The vertical ability calculation divides by mode timing and dimensions; invalid CRTC modes should be impossible but are a dependency.
- Coarse scaling changes `src_w/src_h` before fine scale computation; visual quality and exact phase behavior need hardware validation.
- Chroma phase handling is split between this file and `sun8i_vi_scaler.c`; subsampled crop tests are important.
- `de2_fcc_alpha` uses a global alpha register, so multiple users of that global hardware path could interact if not constrained by mixer design.

## Test Signals

Tests should cover RGB/YUV formats, DE2 vs DE3+ format lists, alpha property presence, color encoding/range properties, chroma subsampled source offsets, scaler disable/enable decisions, coarse scaling thresholds, CSC configuration calls, multi-plane DMA pitch/address programming, and scanline-limit handling.
