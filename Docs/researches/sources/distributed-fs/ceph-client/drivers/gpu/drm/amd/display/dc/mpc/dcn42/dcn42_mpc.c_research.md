# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c

## Purpose
This file implements the DCN4.2 MPC function table and RMCM-specific operations. It inherits most DCN4.01 and DCN3.2 behavior but adds DCN4.2 blend defaults, wider alpha/gain programming through `MPCC_CONTROL2`, RMCM shaper/3D LUT fast-load control, RMCM 3D LUT size, bias/scale, bit-depth configuration, and enhanced MPCC state readback for RMCM debugging.

## Important APIs, types, and functions
Key functions are `mpc42_init_mpcc`, `mpc42_update_blending`, `mpc42_power_on_rmcm_shaper_3dlut`, `mpc42_configure_rmcm_shaper_lut`, `mpc42_program_rmcm_shaper_luta_settings`, `mpc42_program_rmcm_shaper_lutb_settings`, `mpc42_program_rmcm_shaper_lut`, `mpc42_enable_3dlut_fl`, `mpc42_update_3dlut_fast_load_select`, `mpc42_populate_rmcm_lut`, `mpc42_program_rmcm_lut_read_write_control`, `mpc42_program_lut_mode`, `mpc42_program_rmcm_3dlut_size`, `mpc42_program_rmcm_3dlut_fast_load_bias_scale`, `mpc42_program_rmcm_bit_depth`, `mpc42_set_fl_config`, `mpc42_read_mpcc_state`, and `dcn42_mpc_construct`.

## Control flow and state
Construction initializes `struct dcn42_mpc`, assigns `dcn42_mpc_funcs`, and seeds MPCC defaults with 12-bit global alpha/gain. Blending writes mode fields to `MPCC_CONTROL`, alpha/gain to `MPCC_CONTROL2`, and per-plane gain registers, then mirrors the config in software. RMCM shaper programming powers memory, selects RAM A/B, writes region metadata if present, streams packed PWL samples, then powers memory down. Fast-load setup disconnects, prepares write masks, programs bit depth, RAM bank, bias/scale, 3D LUT size/mode, connects to a HUBP, and enables RMCM routing.

## Dependencies and integration points
The file depends on `dcn42_mpc.h`, `dcn401_mpc` helpers through the function table, generic `mpc.h`, register helpers, and common color conversion support. It fills the nested `.rmcm` callback table inside `struct mpc_funcs`, while retaining DCN401 generic MCM callbacks for the existing MCM path.

## State and persistence behavior
State spans software MPCC blend config, legacy MCM registers, and RMCM registers. `mpc42_read_mpcc_state` extends base MPCC readback with RMCM 3D LUT memory power, mode, read/write control, norm factor, fast-load select/status, bias/scale, shaper power/mode/write state, offsets/scales, region fields, and RMCM routing control. No durable persistence is provided.

## Risks
Only MPCC instances below 2 get RMCM state readback. Fast-load control has sequencing comments documenting required clock and memory behavior, but this file does not manage external pipe clock gating itself. `mpc42_enable_3dlut_fl` hardcodes RMCM connection value 0 when enabled and 0xf when disabled. RMCM LUT population currently covers shaper PWL, while 3D LUT content is expected through fast-load/config paths. Power status failures break to debugger instead of returning an error.

## Test signals
Strong validation signals include blend alpha/gain correctness at 12-bit values, RMCM memory power wait success, shaper bank switching, fast-load enable/disable and HUBP select, 3D LUT size for 17x17x17 and 33x33x33-style enum paths, bias/scale and 10-bit/12-bit bit-depth programming, RMCM state dump accuracy, and no underflow flags during fast-load.
