# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/Kbuild

Purpose: kbuild bridge for ARM display subdrivers, currently routing `CONFIG_DRM_KOMEDA` into the `komeda/` subdirectory.

Important APIs/types/functions: single kbuild rule `obj-$(CONFIG_DRM_KOMEDA) += komeda/`.

Control flow: when `DRM_KOMEDA` is enabled, kbuild recurses into `drivers/gpu/drm/arm/display/komeda/`; otherwise nothing under this subdirectory is built.

State and persistence: no runtime state. Persistent effect is source-tree-aligned build inclusion for Komeda.

Dependencies/integration: depends on `display/Kconfig` declaring `DRM_KOMEDA` and on the parent ARM DRM Makefile adding `display/` for the same symbol.

Risks: duplicate gating in parent and child build files means a symbol-name mismatch would silently omit the Komeda driver. Test signals: build with `CONFIG_DRM_KOMEDA=y/m`, inspect built-in or module object inclusion, and run `make M=drivers/gpu/drm/arm/display`.
