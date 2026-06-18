# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb.h

## Purpose
Defines MB862xx framebuffer user ioctls, device IDs, core enums, board mode data, private framebuffer state, helper declarations, and register access macros.

## Important APIs, Types, and Functions
- `struct mb862xx_l1_cfg` describes layer-1 capture/overlay source, destination, scale, and mirror parameters.
- `MB862XX_L1_GET_CFG`, `MB862XX_L1_SET_CFG`, `MB862XX_L1_ENABLE`, and `MB862XX_L1_CAP_CTL` are fbdev ioctl commands.
- `enum gdctype` identifies supported controller families.
- `struct mb862xx_gc_mode` carries default mode, default bpp, VRAM size, clock, and memory mode settings.
- `struct mb862xxfb_par` stores fbdev pointer, device/PCI handles, mapped framebuffer/MMIO windows, per-block register bases, IRQ, type, clock, I2C adapter, capture state, layer config, and pseudo palette.
- `inreg()` and `outreg()` abstract raw vs normal MMIO access depending on Lime configuration.

## Control Flow
The header does not execute, but it shapes all MB862xx driver flow. The main driver allocates `struct mb862xxfb_par` as `fb_info->par`, initializes base pointers, and uses access macros throughout.

## State and Persistence
`struct mb862xxfb_par` is the central persistent runtime state for each framebuffer instance. It stores mapped resources, hardware subtype, capture buffer offsets, current layer-1 config, and color palette.

## Dependencies and Integration Points
Integrates user ABI ioctls with `mb862xxfbdrv.c`, optional I2C hooks with `mb862xx-i2c.c`, acceleration initialization with `mb862xxfb_accel.c`, and PCI/platform hardware IDs with kernel bus matching.

## Risks
The ioctl definitions pass pointer-typed structure arguments in `_IOR/_IOW`, which is unusual ABI shape. The header has a compile-time conflict guard for mutually exclusive Lime and PCI GDC configs. Register access macros rely on a local variable named `par`, constraining call-site style.

## Test Signals
Compile both Lime and PCI configurations separately, including I2C on/off. Runtime validation includes successful ioctl copy paths, correct mapped register base setup for each `gdctype`, and no accidental simultaneous Lime/PCI config.
