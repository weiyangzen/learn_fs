# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/Makefile

## Purpose
Build recipe for the TI Keystone/TIDSS DRM driver object. It lists all component objects that are linked into `tidss.o` and binds that aggregate to `CONFIG_DRM_TIDSS`.

## Important APIs, Types, And Functions
`tidss-y` includes `tidss_crtc.o`, `tidss_drv.o`, `tidss_encoder.o`, `tidss_kms.o`, `tidss_irq.o`, `tidss_plane.o`, `tidss_scale_coefs.o`, `tidss_dispc.o`, and `tidss_oldi.o`. `obj-$(CONFIG_DRM_TIDSS) += tidss.o` connects the aggregate object to the Kconfig option.

## Control Flow
There is no runtime flow. Kbuild collects listed objects into `tidss.o`; when `CONFIG_DRM_TIDSS` is `m`, the result becomes a module, and when `y`, it is built into the kernel.

## State And Persistence
Persistent build state is determined by Kbuild outputs and the kernel configuration. The Makefile itself stores the authoritative object composition for the driver.

## Dependencies And Integration Points
The object list reflects driver layering: CRTC, plane, encoder, KMS/device glue, IRQ handling, scaling coefficients, DISPC hardware access, and OLDI output support. It integrates with the parent DRM Kbuild tree through `obj-*`.

## Risks And Maintenance Notes
Adding or removing source files without updating `tidss-y` can produce missing symbols or dead code. Object order is usually not semantically important but can affect initcall/link diagnostics. New optional features may need conditional object inclusion rather than unconditional `tidss-y`.

## Test Signals
Signals are compile/link success for built-in and module builds, presence of all expected symbols in `tidss.o`, and no stale object references after source file renames.
