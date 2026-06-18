<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_plane.c

## Purpose

`atmel_hlcdc_plane.c` implements DRM planes for Atmel HLCDC/XLCDC layers. It handles format support, atomic plane validation, scaling, rotation stride calculation, DMA descriptor allocation/programming, color lookup tables, color-space conversion, blending, discard areas, AHB load balancing, and layer IRQ diagnostics.

## Important APIs, Types, And Functions

- `struct atmel_hlcdc_plane_state`: extends DRM plane state with clipped source/destination geometry, discard rectangle, AHB id, bytes-per-pixel, per-plane DMA offsets/strides, plane count, and allocated DMA descriptors.
- Format tables `atmel_hlcdc_plane_rgb_formats` and `atmel_hlcdc_plane_rgb_and_yuv_formats`.
- `atmel_hlcdc_format_to_plane_mode()`: maps DRM fourcc formats to HLCDC hardware format fields.
- Scaler paths: `atmel_hlcdc_plane_setup_scaler()` for legacy HLCDC with optional PHI coefficients and `atmel_xlcdc_plane_setup_scaler()` for XLCDC luma/chroma factors.
- Atomic helpers: `atmel_hlcdc_plane_atomic_check()`, `_update()`, `_disable()`, state reset/duplicate/destroy.
- Preparation helpers exported to the CRTC: `atmel_hlcdc_plane_prepare_disc_area()` and `atmel_hlcdc_plane_prepare_ahb_routing()`.
- DMA helpers: descriptor pool creation in `atmel_hlcdc_create_planes()`, allocation in `atmel_hlcdc_plane_alloc_dscrs()`, and buffer programming in legacy/XLCDC update callbacks.
- Operation tables `atmel_hlcdc_ops` and `atmel_xlcdc_ops`.

## Control Flow

Plane creation allocates a universal DRM plane for each usable layer descriptor, initializes properties based on layer capabilities, and installs helper funcs. Atomic check clips/scales through DRM helpers, derives integer source/destination geometry, computes per-plane DMA offsets and x/p strides for 0/90/180/270 rotation, swaps source width/height for rotated modes, rejects unsupported scaling or partial-size base layers, and stores derived state. CRTC atomic check then chooses discard and AHB routing. Atomic update writes size/position/scaler, general settings, format, CLUT, buffer addresses/strides, discard registers, and finally enables or updates the layer via the descriptor-selected ops.

## State And Persistence Behavior

Persistent software state includes allocated DMA descriptors for each plane state, per-plane derived geometry and DMA offsets, the controller's descriptor pool, and the `dc->layers[]` mapping. Hardware state persists in layer CFG registers, DMA descriptor rings, CLUT entries, CSC coefficients, scaler coefficients, interrupt masks, enable/update bits, and XLCDC ATTRE update triggers.

## Dependencies And Integration Points

The file depends on DRM atomic helpers, GEM DMA framebuffer helpers, DMA pools, blend/rotation properties, local descriptor/register definitions, and the CRTC's atomic preparation calls. It integrates with the controller IRQ handler through `atmel_hlcdc_plane_irq()`.

## Risks And Edge Cases

DMA descriptors are allocated per atomic state copy; allocation failures can make state duplication fail. Rotation stride math uses negative strides and must account for chroma subsampling. Scaling with alpha formats is rejected because hardware constraints do not allow it. The discard-area optimization only chooses the largest opaque overlay and is intentionally simple. XLCDC updates require writing ATTRE bits for multiple layers, so wrong update masks can leave changes unapplied. Error handling in `anx6345_start`-style sequence is not relevant here, but register writes in this file mostly assume regmap success.

## Test Signals

Atomic plane tests across all supported formats, multi-plane YUV with subsampling, rotations, scaling up/down, alpha blending, CLUT updates, CSC output, discard optimization, AHB routing under multiple planes, DMA descriptor leak checks, layer overrun IRQ logging, and both legacy/XLCDC hardware are important validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_plane.c -->
