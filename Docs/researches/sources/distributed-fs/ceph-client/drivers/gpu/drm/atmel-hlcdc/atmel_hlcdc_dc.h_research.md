<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.h

## Purpose

`atmel_hlcdc_dc.h` is the shared register, type, and cross-file API contract for the Atmel HLCDC/XLCDC DRM driver. It defines layer register offsets/bit fields, DMA descriptors, layer/plane/controller descriptors, operation tables for legacy vs XLCDC variants, and helper accessors.

## Important APIs, Types, And Macros

- Register and bit macros for common HLCDC layer control, IRQ, DMA, format, position/size, alpha/blending, discard area, scaler, CLUT, and XLCDC-specific layer registers.
- `struct atmel_hlcdc_layer_cfg_layout`: per-layer CFG register layout, with zero meaning unsupported.
- `struct atmel_hlcdc_dma_channel_dscr`: hardware DMA descriptor ordered as address, control, next, self and aligned to 64 bits.
- `enum atmel_hlcdc_layer_type`, `struct atmel_hlcdc_formats`, `struct atmel_hlcdc_layer_desc`, `struct atmel_hlcdc_layer`, `struct atmel_hlcdc_plane`, and `struct atmel_hlcdc_dc`.
- `struct atmel_lcdc_dc_ops`: legacy/XLCDC operation callbacks for scaling, buffer updates, disable/update, CSC init, and IRQ debug.
- Inline register helpers: layer register/CFG/CLUT read-write and layer initialization.
- Cross-file prototypes for mode validation, plane creation/IRQ/preparation, CRTC IRQ/create, and output creation/bus-format lookup.

## Control Flow

The header only has inline register access helpers. Runtime control flow is supplied by function pointers in `atmel_lcdc_dc_ops`, allowing descriptor-selected code to choose legacy HLCDC or XLCDC implementations at atomic update time.

## State And Persistence Behavior

The declared structures hold the driver's core persistent state: DRM device, active layer descriptors, DMA descriptor pool, CRTC pointer, MFD/regmap pointers, and suspend snapshot. Hardware state persists in layer registers and DMA descriptors that the display controller fetches.

## Dependencies And Integration Points

It depends on regmap and DRM plane types plus MFD register definitions included by C files. All local C files include this header to share SoC descriptors, layer abstractions, and operation callbacks.

## Risks And Edge Cases

The DMA descriptor field order and alignment are hardware ABI requirements. Layout fields using zero as unsupported mean register ID 0 cannot be represented as a configurable CFG slot except where handled separately. Legacy and XLCDC bits overlap semantically but not always numerically, so ops must match descriptor type. Wrong layer offsets or CLUT offsets can corrupt unrelated hardware registers.

## Test Signals

Compile all local C files, run static checks around descriptor/layout initialization, validate DMA descriptor alignment, exercise both `atmel_hlcdc_ops` and `atmel_xlcdc_ops`, and inspect register traces on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.h -->
