# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/Makefile

Purpose: maps ARM DRM Kconfig symbols to built objects and subdirectories.

Important APIs/types/functions: object variables are `hdlcd-y`, `mali-dp-y`, `obj-$(CONFIG_DRM_HDLCD)`, `obj-$(CONFIG_DRM_MALI_DISPLAY)`, and `obj-$(CONFIG_DRM_KOMEDA)`. HDLCD links `hdlcd_drv.o` and `hdlcd_crtc.o`; Mali DP links driver, hardware, plane, CRTC, and memory-writeback objects; Komeda descends into `display/`.

Control flow: kbuild evaluates enabled symbols and either links composite objects or enters the Komeda display subdirectory. The file is declarative and has no runtime execution.

State and persistence: persistent output is kernel object/module composition. The `mali-dp` module name follows the composite object name; Komeda is built through `display/komeda/Makefile`.

Dependencies/integration: consumes symbols from `drivers/gpu/drm/arm/Kconfig` and `drivers/gpu/drm/arm/display/Kconfig`. It participates in the parent DRM build tree.

Risks: object-list drift causes missing functions at link time or dead code. Adding Komeda objects here instead of under `display/` would break the current source-tree separation. Test signals: `make M=drivers/gpu/drm/arm`, allmodconfig link checks, and verifying module object names match Kconfig help text.
