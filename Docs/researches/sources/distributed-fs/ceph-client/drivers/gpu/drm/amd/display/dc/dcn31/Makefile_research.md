# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/Makefile

Purpose: Adds DCN31-specific display core objects to the AMD display build.

Important APIs/types/functions: Defines `DCN31 = dcn31_panel_cntl.o dcn31_apg.o dcn31_afmt.o dcn31_vpg.o`, prefixes with `$(AMDDALPATH)/dc/dcn31/`, and appends to `AMD_DISPLAY_FILES`.

Control flow: Build-time list expansion only.

State/persistence: Persists the object set included for DCN31 display support.

Dependencies/integration: Included by the larger AMD DC make hierarchy. The object list provides panel control, APG audio packet generation, AFMT audio formatting, and VPG packet generation support.

Risks: Missing or stale object names cause link-time failures or absent hardware hooks. The list must stay aligned with resource constructors that reference these modules.

Test signals: A configured AMD display build should compile and link all four DCN31 objects.
