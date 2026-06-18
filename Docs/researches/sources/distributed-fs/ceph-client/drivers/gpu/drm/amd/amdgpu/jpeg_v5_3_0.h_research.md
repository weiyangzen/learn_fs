<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.h

Purpose: provides small JPEG 5.3.0-specific register constants for DPG SRAM programming and exports the `jpeg_v5_3_0_ip_block` descriptor.

Important APIs and constants: defines DPG-space register IDs for JPEG clock-gating gate/control, system interrupt enable, no-op command, and GFX10 address configuration. The implementation uses these with `ADD_SOC24_JPEG_TO_DPG_SRAM()` and `WREG32_SOC24_JPEG_DPG_MODE()` during dynamic power-gating startup. It also declares `extern const struct amdgpu_ip_block_version jpeg_v5_3_0_ip_block`.

Control flow and integration: no executable logic. Constants bridge normal generated SOC15 register names and the SOC24 JPEG DPG programming path.

State and persistence behavior: no state is stored. DPG SRAM and hardware registers are mutated by the `.c` file using these constants.

Dependencies: requires AMDGPU IP block declarations and the JPEG/VCN DPG helper macros available in the implementation context.

Risks and test signals: risks include DPG address mismatch causing PSP SRAM updates to program the wrong register and the closing include-guard comment incorrectly referring to `__JPEG_V5_0_0_H__`. Test by entering DPG mode, verifying clock-gating and interrupt DPG writes take effect, and compiling `jpeg_v5_3_0.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.h -->
