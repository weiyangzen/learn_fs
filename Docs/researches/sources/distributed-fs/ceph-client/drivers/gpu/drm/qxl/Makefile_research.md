# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/Makefile

Purpose: This Makefile defines the QXL DRM driver object composition.

Important APIs, types, and functions: `qxl-y` lists all translation units: driver entry, KMS/display, TTM/object/GEM, command/image/draw/debugfs/IRQ/dumb/ioctl/release/PRIME. `obj-$(CONFIG_DRM_QXL) += qxl.o` binds the aggregate object to Kconfig.

Control flow: Build-time only. Kbuild compiles each listed `.o` and links them into `qxl.o` when `DRM_QXL` is enabled.

State and persistence: No runtime state. The file controls which code participates in the module.

Dependencies and integration points: Mirrors the split declarations in `qxl_drv.h`; adding or removing a source file must stay synchronized with exported prototypes and driver feature registration.

Risks: Missing an object silently becomes a link failure for referenced symbols, while stale objects can retain dead code. Because QXL spans many tightly coupled files, object-list drift is high impact.

Test signals: `make drivers/gpu/drm/qxl/` for module and built-in configurations; inspect `qxl.o` symbol resolution for all functions declared in `qxl_drv.h`.
