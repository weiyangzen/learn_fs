## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_jpeg.h

Purpose: declares shared JPEG engine data structures, DPG register access macros, capabilities, RAS state, lifecycle APIs, diagnostics, and CS parser entry point.

Important APIs/types: constants bound JPEG instances/rings and legal register ranges. DPG macros (`WREG32_SOC15_JPEG_DPG_MODE`, `RREG32_SOC15_JPEG_DPG_MODE`, SOC24 variants, and SRAM append macro) abstract direct versus indirect SRAM programming. `struct amdgpu_jpeg_inst` holds decoder rings, IRQ sources, DPG SRAM BO/address/pointer, pause state, and AID ID. `struct amdgpu_jpeg` stores instance count, internal/external register maps, harvest config, delayed idle work, power-gating lock, submission count, RAS state, DPG mode, reset/cap flags, and register dump metadata.

Control flow contract: version-specific JPEG implementations populate instances, rings, register maps, IRQ funcs, and call shared lifecycle helpers. Submit paths should call begin/end use around work to keep power gating correct. CS paths call `amdgpu_jpeg_dec_parse_cs()` before scheduling user packets.

State and persistence: all state is per-device runtime state. DPG SRAM BOs persist for driver lifetime and are freed in shared fini. Register dump memory persists only for diagnostics.

Dependencies/integration: includes RAS and CS parser headers, expects `amdgpu_device`, `amdgpu_ring`, `amdgpu_ip_block`, `drm_printer`, and firmware ID definitions from broader AMDGPU headers.

Risks: register access macros reference `adev` implicitly, so they must be used in scopes where that name exists. The SOC15 indirect macro can append to `dpg_sram_curr_addr` without explicit bound checks in the macro. JPEG register range constants are security-relevant for parser validation and must track hardware packet permissions.

Test signals: build coverage for SOC15/SOC24 users, parser fuzz/negative tests, DPG SRAM programming tests, multi-instance/multi-ring scheduling, and IP dump output.
