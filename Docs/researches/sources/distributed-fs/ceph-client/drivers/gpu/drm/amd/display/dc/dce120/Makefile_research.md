## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/Makefile

Purpose: Kbuild fragment adding the DCE120 timing-generator implementation to AMD display builds.

Important variables: `CFLAGS_$(AMDDALPATH)/dc/dce120/dce120_resource.o = -Wno-override-init`, `DCE120 = dce120_timing_generator.o`, `AMD_DAL_DCE120`, and `AMD_DISPLAY_FILES += $(AMD_DAL_DCE120)`.

Control flow and integration: the parent build includes this fragment, object names are prefixed with the DCE120 directory, and the resulting object list links into the AMD display module. No runtime state exists.

Risks and test signals: omission would remove DCE120 TG support at link time. Build tests with DCE120 resource code and symbol references to `dce120_timing_generator_construct` are the key checks.
