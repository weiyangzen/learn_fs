## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/Makefile

Purpose: Kbuild fragment for the DCE112 display controller subdirectory. It adds the DCE112 compressor object to `AMD_DISPLAY_FILES`.

Important variables: `CFLAGS_$(AMDDALPATH)/dc/dce112/dce112_resource.o = -Wno-override-init`, `DCE112 = dce112_compressor.o`, `AMD_DAL_DCE112`, and `AMD_DISPLAY_FILES += $(AMD_DAL_DCE112)`.

Control flow and integration: when included by the parent AMD display build, the fragment prefixes object paths with `$(AMDDALPATH)/dc/dce112/` and appends them to the global display object list. No runtime state exists.

Risks and test signals: missing objects here silently remove DCE112 compressor support. Build coverage with DCE112 enabled and link checks for compressor symbols are the primary signals.
