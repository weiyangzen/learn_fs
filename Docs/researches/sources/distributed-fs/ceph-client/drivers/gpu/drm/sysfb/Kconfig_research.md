# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/Kconfig

## Purpose

`sysfb/Kconfig` declares the DRM firmware/system framebuffer driver menu. It configures the shared helper module and concrete coreboot, EFI, Open Firmware, simple framebuffer, and VESA DRM drivers.

## Important APIs, Types, and Definitions

- `menu "Drivers for system framebuffers"` depends on `DRM`.
- `DRM_SYSFB_HELPER`: hidden tristate selected by concrete drivers.
- `DRM_COREBOOTDRM`: coreboot framebuffer DRM driver.
- `DRM_EFIDRM`: EFI framebuffer DRM driver, gated by EFI and `!SYSFB_SIMPLEFB || COMPILE_TEST`.
- `DRM_OFDRM`: Open Firmware display driver, gated by OF and PPC or compile test.
- `DRM_SIMPLEDRM`: generic simple platform-provided framebuffer DRM driver.
- `DRM_VESADRM`: x86 VESA framebuffer DRM driver, gated by x86 and `!SYSFB_SIMPLEFB || COMPILE_TEST`.

## Control Flow and State

Kconfig selection controls which object files are built and which helper subsystems are selected. All concrete drivers select `APERTURE_HELPERS`, DRM client selection, shmem GEM helpers, KMS helpers, and `DRM_SYSFB_HELPER`. EFI and VESA also select `SYSFB` because they consume firmware screen-info platform devices.

## Dependencies and Integration Points

This file integrates with Linux Kconfig, DRM core helpers, sysfb/simplefb infrastructure, architecture firmware paths, and module build selection in the Makefile.

## Risks and Edge Cases

- EFI/VESA are mutually constrained with `SYSFB_SIMPLEFB` except under compile testing; configuration changes can alter which firmware framebuffer driver binds first.
- Hidden `DRM_SYSFB_HELPER` must be selected by every driver using helper symbols.
- Platform constraints are conservative; relaxing them requires build and runtime validation on affected architectures.

## Test Signals

Run allmodconfig/allyesconfig and targeted configs for coreboot, EFI, OF/PPC, simpledrm, and VESA. Verify module dependencies and no unresolved helper symbols. Boot tests should confirm only the intended system framebuffer driver binds for each firmware path.
