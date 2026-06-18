# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c

## Purpose
`nbio_v7_0.c` implements NBIO 7.0 support for early SOC15/Navi-adjacent devices. It provides basic memory/revision access, SDMA/VCN/IH doorbell programming, HDP flush mapping, SYSHUB-assisted clock gating, light sleep control, and a small init workaround for NBIO `2.5.0`.

## Important APIs, Types, And Functions
Exports are `nbio_v7_0_hdp_flush_reg` and `nbio_v7_0_funcs`. Notable helpers include `nbio_7_0_read_syshub_ind_mmr()`, `nbio_7_0_write_syshub_ind_mmr()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, `ih_control()`, `init_registers()`, and `set_reg_remap()`.

## Control Flow
Hardware init programs remap state, runs `init_registers()`, remaps HDP flush registers, and enables doorbell aperture. Clock gating writes both NBIF LCLK and indirect SYSHUB SOCCLK/SHUBCLK registers. Doorbell setup programs two SDMA ranges, one MMSCH/VCN range, and an IH range. Self-ring aperture callback is intentionally empty for this generation.

## State And Persistence
State is volatile NBIO, PCIE, SYSHUB, and MMIO-remap configuration. `set_reg_remap()` uses the generic MMIO hole on bare metal and HDP coherency flush offset in VF or large-page cases.

## Dependencies And Integration Points
It depends on generated NBIO 7.0 register files, Vega10 enum definitions, KFD remap constants, and SOC15 common init.

## Risks
The empty self-ring aperture callback means late common init can call it without effect. Clock-gating state reporting reads `smnCPM_CONTROL` while enablement uses NBIF/SYSHUB paths, so state flags may not cover every programmed bit. The `2.5.0` strap workaround is narrow and should be tested on that IP only.

## Test Signals
Useful tests are SDMA/VCN/IH ring startup, HDP flush remap reads, clock-gating flag transitions, and NBIO `2.5.0` reset behavior after the strap bit clear.
