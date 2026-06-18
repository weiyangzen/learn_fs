# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v9_0.c

Purpose: SMUIO v9 operation table for ROM index/data offsets and ROM clock-gating control.

Important APIs, types, and functions: defines `smuio_v9_0_funcs` with ROM offset callbacks, `update_rom_clock_gating`, and `get_clock_gating_state`.

Control flow: ROM helpers return SOC15 offsets for `mmROM_INDEX` and `mmROM_DATA`. Clock-gating update skips APUs, clears ROM soft overrides when enabling supported MGCG, and sets overrides otherwise. Query reads override0 to report ROM MGCG.

State and persistence: state is hardware `mmCGTT_ROM_CLK_CTRL0` and software feature flags in `adev`; no persistent storage.

Dependencies and integration points: used by generic ROM/VBIOS and CG reporting paths for SMUIO v9 ASICs.

Risks and test signals: APU register avoidance is required. Query only checks one override bit. Test signals are VBIOS access, CG flag reporting, and safe operation on APU/discrete variants.
