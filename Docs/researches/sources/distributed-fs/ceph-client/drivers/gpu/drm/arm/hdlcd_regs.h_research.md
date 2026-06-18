# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_regs.h

## Purpose

`hdlcd_regs.h` is the ARM HDLCD register and bit-definition header. It names MMIO offsets for version, interrupt, framebuffer, bus, timing, polarity, command, pixel-format, and color-select registers, plus constants for product identification, interrupt bits, polarity bits, command bits, bus options, and maximum resolution.

## Important APIs, Types, And Macros

Key register offsets include `HDLCD_REG_VERSION`, `HDLCD_REG_INT_*`, `HDLCD_REG_FB_BASE`, `HDLCD_REG_FB_LINE_LENGTH`, `HDLCD_REG_FB_LINE_COUNT`, `HDLCD_REG_FB_LINE_PITCH`, `HDLCD_REG_BUS_OPTIONS`, vertical/horizontal timing registers, `HDLCD_REG_POLARITIES`, `HDLCD_REG_COMMAND`, `HDLCD_REG_PIXEL_FORMAT`, and RGB select registers. Important masks include `HDLCD_PRODUCT_ID`, `HDLCD_PRODUCT_MASK`, version masks, `HDLCD_INTERRUPT_*`, `HDLCD_DEBUG_INT_MASK`, `HDLCD_POLARITY_*`, `HDLCD_COMMAND_ENABLE`, `HDLCD_BYTES_PER_PIXEL_MASK`, bus burst constants, `HDLCD_MAX_XRES`, and `HDLCD_MAX_YRES`.

## Control Flow

The header has no runtime control flow. It is consumed by driver code that validates the product register, installs/acknowledges interrupts, programs framebuffer DMA layout, programs display timings, configures signal polarities, enables/disables the controller, and selects pixel component extraction.

## State And Persistence Behavior

No software state is stored here. The macros describe hardware stateful registers. Writes to timing, bus, framebuffer, pixel-format, and command registers persist until subsequent driver writes, hardware reset, or power loss. Interrupt status/clear/mask registers have side-effect semantics that callers must respect.

## Dependencies And Integration Points

The file is paired with `hdlcd_drv.c` and `hdlcd_crtc.c`. It depends only on the C preprocessor and basic integer constants. It integrates with DRM mode programming by translating DRM timing and format state into HDLCD MMIO fields.

## Risks And Edge Cases

Register values include minus-one encoded dimensions in consumers, so valid ranges must be enforced before writes. Interrupt bits include debug-only signals that should not be confused with the VSYNC vblank mask. `HDLCD_PIXEL_FMT_BIG_ENDIAN` exists but current listed code only programs bytes-per-pixel and component selectors. Maximum resolution is documented as 4096x4096 at 32bpp and should remain synchronized with mode-config limits.

## Test Signals

Useful signals include product ID matching, interrupt-mask and clear behavior on hardware, max-resolution mode rejection/acceptance, all advertised pixel formats producing correct colors, bus burst behavior under high bandwidth, and static comparison against ARM HDLCD hardware documentation.
