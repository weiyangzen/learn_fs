# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.c

## Purpose

`dcn20_dsc.c` is the DCN2.0 hardware backend for DSC encoders. It implements the `struct dsc_funcs` table, translates validated DC DSC configuration into DRM PPS and DSCC register values, writes DSC/DSCC/DSCCIF/DSCRM registers, exposes state reads, and controls enable, disable, disconnect, and PPS packing.

## Important APIs, Types, And Functions

Key functions are `dsc2_construct`, `dsc2_get_enc_caps`, `dsc2_read_state`, `dsc2_read_reg_state`, `dsc2_validate_stream`, `dsc2_set_config`, `dsc2_get_packed_pps`, `dsc2_enable`, `dsc2_disable`, `dsc2_disconnect`, `dsc2_wait_disconnect_pending_clear`, `dsc_prepare_config`, `dsc_override_rc_params`, `dsc_init_reg_values`, and `dsc_update_from_dsc_parameters`.

## Control Flow

Construction installs function pointers and register metadata. Configuration calls `dsc_prepare_config`, which validates slice counts, version, picture size, line-buffer depth, and BPP; initializes defaults; maps pixel format; computes slice dimensions and PPS BPP encoding; calculates RC parameters through `calc_rc_params`; applies optional RC overrides; runs `dscc_compute_dsc_parameters`; and returns OPTC slice/bytes-per-pixel data. `dsc2_set_config` logs and writes every PPS/rate-control register. Enable sets `DSC_CLOCK_EN` and DSCRM forwarding after checking for conflicting OPP routing.

## State, Dependencies, Risks, And Test Signals

State is in hardware registers plus `struct dcn20_dsc::reg_vals`. The file depends on `reg_helper`, `dcn20_dsc.h`, `dscc_types.h`, `rc_calc.h`, and DRM DSC PPS packing. Risks include register field mismatches, picture widths over 5184, invalid slice divisibility, FP-gated RC calculation, and conflicting enable attempts. Tests should validate PPS packing, register values for each pixel format, enable/disable/disconnect sequencing, state readback, and RC overrides.
