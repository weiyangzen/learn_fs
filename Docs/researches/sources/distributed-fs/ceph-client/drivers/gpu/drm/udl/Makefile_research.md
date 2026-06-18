<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Makefile

Purpose: Aggregates the UDL driver object list for kbuild.

Important APIs/types/functions: `udl-y` includes `udl_drv.o`, `udl_edid.o`, `udl_main.o`, `udl_modeset.o`, and `udl_transfer.o`; `obj-$(CONFIG_DRM_UDL) := udl.o`.

Control flow: Kbuild links USB lifecycle, EDID, URB management, modeset, and transfer compression code into one UDL module.

State and persistence: No runtime state.

Dependencies and integration points: Mirrors the module's source-level responsibilities and Kconfig option.

Risks and test signals: Build tests should catch missing object entries if features are split into new files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/Makefile -->
