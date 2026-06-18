# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/Makefile

## Purpose
Builds the Fujitsu MB862xx framebuffer driver object from its main driver and acceleration support, with optional I2C adapter support.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_FB_MB862XX) += mb862xxfb.o` creates the composite driver object.
- `mb862xxfb-y := mb862xxfbdrv.o mb862xxfb_accel.o` always includes main fbdev and acceleration code.
- `mb862xxfb-$(CONFIG_FB_MB862XX_I2C) += mb862xx-i2c.o` conditionally adds the hardware I2C adapter.

## Control Flow
Kbuild links the listed objects into `mb862xxfb.o` only when the driver config is enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates MB862xx source files into the kernel build and reflects the optional I2C integration declared in `mb862xxfb.h`.

## Risks
If `CONFIG_FB_MB862XX_I2C` is disabled, `mb862xx_i2c_init()` compiles to an inline no-op, so boards needing DDC or I2C devices will silently lack that bus.

## Test Signals
Build matrix should cover `CONFIG_FB_MB862XX` on/off and `CONFIG_FB_MB862XX_I2C` on/off, verifying the expected object members.
