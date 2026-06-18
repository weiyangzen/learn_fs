# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_ui_layer.h

## Purpose

`sun8i_ui_layer.h` defines UI layer register address macros, attribute bit fields, alpha mode constants, forward declarations, and the UI plane creation API.

## Important APIs, Types, and Definitions

- `SUN8I_MIXER_CHAN_UI_LAYER_*()`: per-overlay attribute, size, coordinate, pitch, low-address, bottom-address, and fill-color register offsets.
- `SUN8I_MIXER_CHAN_UI_TOP_HADDR()` / `BOT_HADDR()`: high-address register offsets for UI channels.
- `SUN8I_MIXER_CHAN_UI_OVL_SIZE()`: overlay size register offset.
- Attribute bits and masks: enable bit, alpha mode, framebuffer format offset/mask, and alpha value field.
- `sun8i_ui_layer_init_one()`: external constructor for UI planes.

## Control Flow and State

The header is a register contract. Runtime control flow is in `sun8i_ui_layer.c`; consumers use these macros to compute offsets from a mixer channel base and overlay index. The macros assume the hardware's 0x20-byte per-layer stride and fixed channel register layout.

## Dependencies and Integration Points

It includes DRM plane declarations and forward-declares `struct sun8i_mixer` and `struct sun8i_layer`. It depends on `BIT()`/`GENMASK()` visibility through included kernel headers and integrates with the mixer register map, DRM plane initialization, and alpha property handling.

## Risks and Edge Cases

- Register macros do not validate overlay indices; callers must ensure the target layer exists.
- Alpha constants must match hardware encoding and the C file's property programming.
- High-address registers are defined but not programmed by the UI layer implementation in this subset, which matters for DMA addresses above 32 bits.

## Test Signals

Compile tests should catch constructor signature drift. Register-level tests should validate each macro against hardware documentation or known-good traces, especially address stride and alpha/format fields.
