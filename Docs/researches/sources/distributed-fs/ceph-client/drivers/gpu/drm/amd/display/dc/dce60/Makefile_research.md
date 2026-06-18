## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/Makefile

Purpose: Kbuild fragment adding the DCE60 timing-generator implementation to AMD display builds.

Important variables: `CFLAGS_$(AMDDALPATH)/dc/dce60/dce60_resource.o = -Wno-override-init`, `DCE60 = dce60_timing_generator.o`, `AMD_DAL_DCE60`, and `AMD_DISPLAY_FILES += $(AMD_DAL_DCE60)`.

Control flow and integration: the parent build includes this file, prefixes DCE60 object paths, and appends them to the display object list. Runtime behavior is in the compiled timing-generator object.

Risks and test signals: if not included, DCE60 resource code cannot link its TG constructor. Build tests for DCE60 configurations are the main signal.
