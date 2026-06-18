# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0.c

Purpose: SMUIO v11 function table for ROM register offsets and ROM memory clock-gating control.

Important APIs, types, and functions: defines `smuio_v11_0_funcs` with `get_rom_index_offset`, `get_rom_data_offset`, `update_rom_clock_gating`, and `get_clock_gating_state`. Helpers use SMUIO 11.0.0 generated offsets and masks.

Control flow: ROM offset helpers return SOC15 register offsets. Clock-gating update exits for APUs or unsupported `AMD_CG_SUPPORT_ROM_MGCG`; otherwise it clears soft override bits to enable gating or sets them to disable gating. State query reads the same register and reports ROM MGCG when override0 is clear.

State and persistence: state is the `mmCGTT_ROM_CLK_CTRL0` hardware register and feature flags in `adev->cg_flags`. No software persistence exists.

Dependencies and integration points: consumed through `adev->smuio.funcs` by ROM/VBIOS access and clock-gating reporting code. Depends on SOC15 access macros and generated SMUIO register headers.

Risks and test signals: APU paths must avoid unavailable registers. State reporting checks only override0, while update controls override0 and override1. Test signals are VBIOS ROM access offsets, clock-gating debug flags, and no register faults on APUs.
