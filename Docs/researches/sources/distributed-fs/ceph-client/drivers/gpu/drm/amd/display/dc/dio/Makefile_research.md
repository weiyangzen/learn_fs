# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/Makefile

Purpose: Aggregates AMD DC Display I/O objects for virtual encoders and multiple DCN hardware generations.

Important APIs/types/functions: Always adds `virtual_link_encoder.o` and `virtual_stream_encoder.o`. Under `CONFIG_DRM_AMD_DC_FP`, it adds DCN10, DCN20, DCN30, DCN301, DCN31, DCN314, DCN32, DCN35, DCN321, DCN401, and DCN42 DIO object lists to `AMD_DISPLAY_FILES`.

Control flow: Build-time conditional expansion based on `CONFIG_DRM_AMD_DC_FP`.

State/persistence: Persists the set of DIO objects linked into the driver for a configuration.

Dependencies/integration: Relies on `AMDDALPATH` and the parent AMD display make system. The floating-point config gate controls physical DCN DIO implementations while virtual encoders remain available.

Risks: A missing object here silently removes a generation-specific encoder implementation from builds. The broad `CONFIG_DRM_AMD_DC_FP` gate means non-FP builds do not get the physical DCN DIO modules.

Test signals: Build logs/object lists should show virtual objects unconditionally and generation-specific objects only with `CONFIG_DRM_AMD_DC_FP=y`.
