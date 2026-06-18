# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/Kconfig

Purpose: defines the DRM "ARM devices" menu and build-time configuration for ARM HDLCD, legacy Mali Display Processor, and sourced Komeda display support.

Important APIs/types/functions: Kconfig symbols are `DRM_HDLCD`, `DRM_HDLCD_SHOW_UNDERRUN`, `DRM_MALI_DISPLAY`, and sourced `drivers/gpu/drm/arm/display/Kconfig` for `DRM_KOMEDA`. Symbols select DRM client setup, KMS helpers, GEM DMA helpers, bridge support for HDLCD, and videomode helpers for Mali display drivers.

Control flow: Kconfig dependency resolution determines which modules/objects the Makefiles build. `DRM_HDLCD` and `DRM_MALI_DISPLAY` require `DRM`, `OF`, ARM/ARM64/COMPILE_TEST, and `COMMON_CLK`; Komeda is sourced separately but remains under the DRM-dependent ARM menu.

State and persistence: no runtime state. Its persistent effect is the generated kernel `.config`, module availability, and compile coverage for the driver family.

Dependencies/integration: integrates ARM DRM drivers into the global DRM build. It feeds `drivers/gpu/drm/arm/Makefile` and `display/Kbuild`.

Risks: missing selects can produce link failures or partial feature exposure. Broad `COMPILE_TEST` support can expose architecture assumptions. Incorrect dependency tightening can silently drop display drivers from builds. Test signals: Kconfig `olddefconfig`, ARM/ARM64 and COMPILE_TEST builds, module-name checks for `hdlcd`, `mali-dp`, and `komeda`, and verifying selected helper libraries appear in `.config`.
