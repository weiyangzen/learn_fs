# sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/Makefile

Purpose: Kbuild fragment for the S3 Savage framebuffer driver. It declares the composite `savagefb.o` object and conditionally includes optional I2C/DDC and acceleration implementation files.

Important APIs/types/functions: the important build symbols are `CONFIG_FB_SAVAGE`, `CONFIG_FB_SAVAGE_I2C`, and `CONFIG_FB_SAVAGE_ACCEL`. `savagefb-y` always includes `savagefb_driver.o`; `savagefb-$(CONFIG_FB_SAVAGE_I2C)` adds `savagefb-i2c.o`; `savagefb-$(CONFIG_FB_SAVAGE_ACCEL)` adds `savagefb_accel.o`.

Control flow: there is no runtime flow. Kbuild links only the selected objects into `savagefb.o`, which means functions declared in `savagefb.h` are either provided by optional objects or compiled out by preprocessor fallbacks in the main driver/header.

State and persistence: no runtime state. The persistent effect is the build-time composition of driver capabilities.

Dependencies and integration: included from the fbdev build tree when `drivers/video/fbdev/Makefile` descends into the Savage directory. It relies on Kconfig selecting optional I2C and acceleration symbols consistently with preprocessor guards in the C sources.

Risks: if Kconfig allows code paths that call optional symbols without the corresponding object, link failures would occur; this is partly mitigated by `#if defined(CONFIG_FB_SAVAGE_I2C)` blocks and non-accel fallbacks. The object order makes the main driver the base unit.

Test signals: kernel builds with `CONFIG_FB_SAVAGE` alone, with I2C only, with acceleration only, with both options, and with the driver disabled.
