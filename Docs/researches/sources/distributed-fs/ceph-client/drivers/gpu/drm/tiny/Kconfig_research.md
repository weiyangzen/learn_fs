# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/Kconfig

## Purpose

`tiny/Kconfig` lists configuration entries for small DRM drivers, including the Apple Touch Bar DRM driver in this work item. It controls build-time availability and helper dependencies for USB, PCI, SPI, and simple panel/display devices.

## Important APIs, Types, and Functions

- `DRM_APPLETBDRM` is a tristate option for Apple Touch Bar display support. It depends on `DRM`, `USB`, `MMU`, and `X86 || COMPILE_TEST`, and selects SHMEM GEM and KMS helpers.
- The file also defines options for ARC PGU, Bochs, Cirrus QEMU, GM12U320, MIPI DBI panels, Pixpaper, HX8357D, ILI9163, ILI9225, ILI9341, ILI9486, MI0283QT, RePaper, and Sharp Memory LCD drivers.

## Control Flow

Kconfig selections drive the tiny DRM Makefile. Enabling `DRM_APPLETBDRM` compiles `appletbdrm.o` and provides a USB DRM driver module named `appletbdrm`.

## State and Persistence Behavior

Configuration choices persist in the kernel build. Selected helper dependencies determine which DRM memory-management and KMS APIs are available to the compiled driver.

## Dependencies and Integration Points

`DRM_APPLETBDRM` integrates with USB and DRM SHMEM/KMS helper infrastructure and is limited to x86 runtime platforms unless compile-testing. Other entries select helpers appropriate to their buses and memory models.

## Risks and Edge Cases

- `DRM_APPLETBDRM` does not select `DRM_CLIENT_SELECTION`, so automatic fbdev/client behavior depends on generic DRM behavior and explicit setup in the driver, which this file does not provide.
- Tiny drivers share one Kconfig file; dependency edits can unintentionally affect unrelated drivers.
- Mixed indentation appears in the Pixpaper entry, which is cosmetic but can distract from Kconfig style consistency.

## Test Signals

Build tests should cover `DRM_APPLETBDRM=y/m/n`, x86 and `COMPILE_TEST` builds, USB disabled builds, and allmodconfig interactions with other tiny DRM entries.
