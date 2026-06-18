# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn35/dcn35_dpp.c

## Purpose
`dcn35_dpp.c` adapts DCN32 DPP behavior for DCN 3.5. It adds DPP clock-control handling for DISPCLK_R gate workarounds, programs FCNV bias/scale registers, exposes an FGCg control helper, and installs a DCN35-specific function table.

## Important APIs, types, and functions
- `dpp35_dppclk_control()` enables/disables DPP clocking, optionally programming `DPPCLK_RATE_CONTROL` or `DISPCLK_R_GATE_DISABLE`.
- `dpp35_program_bias_and_scale_fcnv()` writes FCNV floating-point bias/scale registers or resets them to default bias 0 and scale `0x1F000`.
- `dpp35_construct()` delegates most construction to `dpp32_construct()`, swaps in `dcn35_dpp_funcs`, and enables a cursor-memory workaround on early ASIC revisions.
- `dpp35_set_fgcg()` controls fine-grain clock gating replication disable through `DPP_FGCG_REP_DIS`.
- `dcn35_dpp_funcs` inherits DCN32/DCN30 behavior while enabling bias/scale and the DCN35 DPP clock callback.

## Control flow
Construction first calls `dpp32_construct()` with casts from DCN35 shift/mask structures to DCN3 base structures. It then replaces the function table and, when `hw_internal_rev < 0x40`, sets `dispclk_r_gate_disable` so later clock-enable calls program the workaround. Clock control writes `DPP_CONTROL` differently depending on whether the register table exposes `DPPCLK_RATE_CONTROL` and whether the workaround flag is set. Bias/scale programming branches on `bias_and_scale_valid` to either write caller values or restore neutral defaults.

## State and persistence behavior
The only new software state is `dpp->dispclk_r_gate_disable`, stored in the reused `struct dcn3_dpp`. Hardware state is DPP control, FCNV bias/scale, and FGCg control registers. There is no persistent storage beyond runtime registers and object fields.

## Dependencies and integration points
The file depends on `dcn35_dpp.h`, DCN32 construction, inherited DCN30 CM/CNVC helpers, and DCN20-style register fields via casts. It integrates with resource construction through `dpp35_construct()` and with clock/power sequencing through the `dpp_dppclk_control` callback.

## Risks and edge cases
The shift/mask casts require `struct dcn35_dpp_shift` and mask layout to embed the DCN3 field list compatibly. Clock control has nested conditional logic without braces in some branches, so maintenance changes can easily alter behavior. The early-revision workaround is keyed only on `hw_internal_rev < 0x40`; incorrect ASIC revision reporting can leave cursor memory stuck or unnecessarily disable gating. FCNV defaults must match hardware neutral scale.

## Test signals
Signals include DCN35 build coverage, DPP enable/disable with and without `DPPCLK_RATE_CONTROL`, early and later ASIC revision coverage for `DISPCLK_R_GATE_DISABLE`, FCNV bias/scale visual tests, FGCg toggling tests, and inherited DPP format/scaler/color tests.
