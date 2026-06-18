# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.c

Purpose: SMUIO v11.0.6 variant operations for ROM offsets and ROM clock gating.

Important APIs, types, and functions: defines `smuio_v11_0_6_funcs` with ROM index/data offset callbacks, clock-gating update, and state query using v11.0.6 generated headers.

Control flow: offset helpers return SOC15 offsets. Clock-gating update skips APUs, clears soft override bits only when enabling and ROM MGCG is supported, and otherwise sets overrides. Query reports ROM MGCG when override0 is clear.

State and persistence: state is hardware register `mmCGTT_ROM_CLK_CTRL0`; software input state is `adev->flags` and `adev->cg_flags`.

Dependencies and integration points: selected by versioned SMUIO setup for ASICs with SMUIO 11.0.6 and used by VBIOS/ROM and CG reporting paths.

Risks and test signals: unlike v11.0, unsupported enable requests explicitly force overrides, which is safer but should match power expectations. Test signals are ROM read offsets, CG flag reporting, and APU register avoidance.
