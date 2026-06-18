# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/Makefile

Purpose: Adds the DCN301 display core object list to the AMD display build.

Important APIs/types/functions: Defines `DCN301 = dcn301_panel_cntl.o`, prefixes it with `$(AMDDALPATH)/dc/dcn301/` into `AMD_DAL_DCN301`, and appends it to `AMD_DISPLAY_FILES`.

Control flow: Makefile expansion only; no runtime flow.

State/persistence: It persists one build-time object selection. The resulting object is linked into the display driver when this directory's make fragment is included.

Dependencies/integration: Integrated by the parent AMD DC make system through `AMD_DISPLAY_FILES`. It assumes `dcn301_panel_cntl.c` is the only DCN301-specific core object in this subset.

Risks: The comment says "Makefile for dcn30" although the path and variables are DCN301; this is cosmetic but can confuse maintenance. Missing objects here would compile out DCN301-specific behavior even when sources exist.

Test signals: Kernel/display-driver build should include `dc/dcn301/dcn301_panel_cntl.o` in `AMD_DISPLAY_FILES`.
