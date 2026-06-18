<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Makefile

## Purpose

This Makefile defines the `gma500_gfx` DRM module composition. It aggregates shared GMA500 code, Poulsbo/MRST/Oaktrail/Cedarview display paths, memory management, power, BIOS parsing, I2C, IRQ, and optional ACPI/fbdev components.

## Important APIs, Types, And Symbols

The main build variable is `gma500_gfx-y`, which includes the subset files `backlight.o`, `cdv_device.o`, `cdv_intel_crt.o`, `cdv_intel_display.o`, `cdv_intel_dp.o`, `cdv_intel_hdmi.o`, `cdv_intel_lvds.o`, `framebuffer.o`, `gem.o`, `gma_device.o`, `gma_display.o`, `gtt.o`, and `intel_bios.o`, plus other driver files. Conditional objects are `opregion.o` for `CONFIG_ACPI` and `fbdev.o` for `CONFIG_DRM_FBDEV_EMULATION`. `obj-$(CONFIG_DRM_GMA500)` builds `gma500_gfx.o`.

## Control Flow

No runtime control flow exists. At build time, Kbuild links all listed objects into one module/built-in object, allowing cross-file callbacks through `psb_ops`, DRM helpers, and shared private structures.

## State And Persistence

The Makefile stores build composition only. Its persistent effect is which driver features are present in the compiled kernel/module.

## Dependencies And Integration Points

It integrates the Kconfig symbol with Linux Kbuild and ties Cedarview, Poulsbo, Oaktrail, GEM/GTT/MMU, power, IRQ, I2C, VBT, and fbdev subsystems into a single driver.

## Risks And Test Signals

Risks include object ordering surprises if initcall/static symbol assumptions appear, missing conditional guards for ACPI/fbdev users, and monolithic linkage hiding unused platform code. Test signals are modular and built-in builds, ACPI on/off, fbdev emulation on/off, and link checks for exported cross-file symbols such as `cdv_chip_ops`, `psb_gem_dumb_create`, and `psb_fbdev_driver_fbdev_probe`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Makefile -->
