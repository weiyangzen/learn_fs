# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/Makefile

Purpose: builds the Komeda DRM driver composite object and sets include paths for shared Mali display headers.

Important APIs/types/functions: `ccflags-y` includes `../include` and the Komeda source directory. `komeda-y` aggregates core driver, device, format, color, pipeline, framebuffer, KMS, CRTC, plane, writeback connector, private object, event, and D71 backend objects. `obj-$(CONFIG_DRM_KOMEDA) += komeda.o` exposes the module/built-in object.

Control flow: kbuild links all listed objects into `komeda.o` when enabled. D71 files are always part of the Komeda object because current compatible strings all use `d71_identify()`.

State and persistence: no runtime state. Build output determines which symbols are available to the module.

Dependencies/integration: depends on `display/Kbuild` and shared include headers. It includes `komeda_wb_connector.o`, which is not in this subset but is part of the writeback integration referenced by KMS and pipeline state.

Risks: omitting a source file creates unresolved symbols or feature loss. Include-path order could mask header-name collisions. Test signals: module link, `modinfo komeda`, and compile coverage after adding new chip backends or KMS files.
