<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Kconfig

## Purpose

This Kconfig entry exposes the Intel GMA500/GMA600/GMA3600/GMA3650 KMS framebuffer DRM driver as `DRM_GMA500`.

## Important APIs, Types, And Symbols

`config DRM_GMA500` is a tristate labeled "Intel GMA500/600/3600/3650 KMS Framebuffer". It depends on `DRM`, `PCI`, `X86`, and `HAS_IOPORT`. It selects DRM client selection, KMS helper, optional fbdev I/O-memory helpers, I2C/bit-banged I2C, and ACPI-related video/backlight/input/platform/WMI support when ACPI is enabled.

## Control Flow

There is no runtime control flow. Build-time selection enables compilation and module availability for the gma500 driver. Dependency selection ensures the old display stack has PCI, x86 I/O port access, I2C/DDC, KMS helpers, and ACPI video/backlight glue available.

## State And Persistence

The file stores no runtime state. Its persistent effect is the kernel configuration value that determines whether `gma500_gfx` is built in, modular, or omitted.

## Dependencies And Integration Points

It integrates with the DRM subsystem menu, PCI/X86 platform support, fbdev emulation, ACPI video/backlight routing, and the Makefile object list for `gma500_gfx.o`.

## Risks And Test Signals

Risks include overly broad `select`s pulling ACPI/WMI support, missing `HAS_IOPORT` for inb/outb users, and stale "experimental" help text. Test signals are `allyesconfig`/`allmodconfig`, X86 builds with and without ACPI/fbdev emulation, module autoload on matching PCI IDs, and absence from non-X86 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Kconfig -->
