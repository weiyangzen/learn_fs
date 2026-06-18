# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/acp/Kconfig

Purpose: controls AMD Audio CoProcessor support as an amdgpu subcomponent.

Important APIs/types/functions: defines boolean `DRM_AMD_ACP` under `DRM_AMDGPU`, selecting `MFD_CORE` and `PM_GENERIC_DOMAINS` when PM is enabled.

Control flow: when enabled, amdgpu includes ACP integration and `acp_hw.o`, providing the ACP DMA engine support needed by I2S-based ALSA audio on APUs.

State/persistence: config-only state.

Dependencies/integration: integrates amdgpu with MFD, PM domains, and the ACP hardware code.

Risks: disabling removes required I2S audio support on ACP APUs; PM-disabled and PM-enabled builds differ.

Test signals: amdgpu builds with ACP on/off and ACP-capable APU boot/audio probing.
