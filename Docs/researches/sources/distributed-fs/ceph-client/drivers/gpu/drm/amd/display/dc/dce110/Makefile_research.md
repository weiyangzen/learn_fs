# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/Makefile

Purpose: defines the DCE110 display core object list for the AMD display build.

Important build variables: it sets a file-specific warning flag for `dce110_resource.o` through `CFLAGS_$(AMDDALPATH)/dc/dce110/dce110_resource.o = -Wno-override-init`. `DCE110` lists object files for timing generator, compressor, OPP regamma/CSC/view, memory input, OPP, and transform view objects. `AMD_DAL_DCE110` prefixes each object with `$(AMDDALPATH)/dc/dce110/`, and `AMD_DISPLAY_FILES += $(AMD_DAL_DCE110)` contributes them to the larger AMD display build.

Control flow: make expansion is straightforward: object names are collected, prefixed, and appended. No conditional logic is present in this file.

State and persistence: no runtime state. Build state is the object-list contribution to the kernel module build graph.

Dependencies and integration: depends on the outer AMD display make infrastructure defining `AMDDALPATH` and consuming `AMD_DISPLAY_FILES`. The object list integrates `dce110_compressor.o` from this subset with neighboring DCE110 hardware blocks.

Risks: missing an object here prevents the corresponding DCE110 implementation from linking; adding stale objects breaks builds. The override-init warning suppression is narrow and should remain tied to `dce110_resource.o`. Test signals include kernel/driver build with DCE110 enabled, object inclusion checks, and ensuring `dce110_compressor.o` remains present while its APIs are referenced.
