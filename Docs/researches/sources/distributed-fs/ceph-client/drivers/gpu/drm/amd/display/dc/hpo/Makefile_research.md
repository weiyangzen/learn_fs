# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/Makefile

Purpose: Adds HPO DP stream/link encoder objects for supported DCN generations to the AMD display build.

Important APIs and build variables: The whole file is guarded by `ifdef CONFIG_DRM_AMD_DC_FP`. It defines object groups for DCN31 (`dcn31_hpo_dp_stream_encoder.o`, `dcn31_hpo_dp_link_encoder.o`), DCN32 (`dcn32_hpo_dp_link_encoder.o`), and DCN42 (`dcn42_hpo_dp_link_encoder.o`), plus a DCN30 path that relies on `HPO_DCN30` being set externally.

Control flow: included by the parent make hierarchy, it appends generation-prefixed object paths to `AMD_DISPLAY_FILES` when floating-point DC support is enabled.

State and persistence: no runtime state. Build state is make variable composition.

Dependencies and integration: integrates the high-performance output encoders used for DP 2.x/128b132b paths. Relies on `AMDDALPATH`, `AMD_DISPLAY_FILES`, and generation-specific object variables.

Risks and test signals: object omission breaks HPO support only on affected ASICs/configurations. Build tests should verify `CONFIG_DRM_AMD_DC_FP=y` includes all intended generation objects and that DCN30's object variable is defined by the including context.
